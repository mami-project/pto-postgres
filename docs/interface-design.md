# Path Transparency Observatory Component and Interface Definitions

The Path Transparency Observatory consists of several notional components: a raw measurement and database storage backend, a query runtime, an analysis runtime, a set of analysis modules, and a web frontend. This document describes the responsibilities of these components, and the interfaces among them. 

## Components

### Raw Measurement Data Storage

Raw measurement data is stored in files of various types on one (or more) plain
filesystems. Each raw measurement data file is associated with a *campaign*,
implemented as a top-level directory in the file system. Each campaign is
associated with a campaign metadata record, and each file is associated with a
file metadata record. These records are JSON objects. A campaign metadata record
must contain the following properties:

- type: a filetype string. This is freeform, and used by analysis modules to
  determine whether they are capable of processing a given file. If the filetype
  string ends with `-bz2`, the file is compressed, and will be decompressed by
  the analysis runtime

Raw measurement metadata is stored in the PTO metadata PostgreSQL database.

### Observation Database(s)

The observation database stores observations, which are four-tuples of interval,
path, condition, and value. Intervals may be moments in time, or ranges of time
with a start and end time inclusive. Paths are sequences of path elements, which
may be IPv4 addresses or prefixes, IPv6 addresses or prefixes, BGP autonomous
system numbers, path segment pseudonyms, or an "unknown" token.

Every observation belongs to exactly one observation set. An observation set is
a group of observations with a shared status and provenance. An observation set
can be in one of N *states*:

- `in_progress`: an observation set has been allocated, and observations are
  actively being written to it by an analysis module.
- `pending_review`: an observation set has been written to the database, and
  requires administrator review before it is made available in the public PTO
  database.
- `public`: an observation set has been made public, but is not yet referenced
  by a query that has been published outside the PTO; future issues with the
  observation set may be handled by deleting it.
- `permanent`: an observation set had been included in the results of a query
  that has been published outside the PTO; future issues with the observation
  set may be handled by deprecating it.
- `deprecated`: a permanent observation set has been discovered to contain
  errors; it can no longer be used in new queries, but may be used in existing,
  published queries.

An observation set has a set of precedents: observation sets or raw measurement
data files from which it is derived. This precedent information is used to
cascade deprecation or deletion.

An observation set is associated with an analyzer; see [below](#analysis-modules).

The observation database backend may use multiple PostgreSQL databases to
segregate `in_progress` and `pending_review` observation sets from `public`,
`permanent`, and `deprecated` ones.

### Metadata Database

The metadata database stores metadata about raw analysis files, the state of the
query queue, the state of the analysis queue, and information about installed
analyzers. It is implemented as a PostgreSQL database.

### Query Runtime

The query runtime runs queries submitted in IQL over PAPI. It stores information
about which queries have been submitted, which queries are running, and which
queries have run, as well as caching query results; this information is stored
in the PTO metadata PostgreSQL database.

Queries are identified by hash of their IQL expression, so identical queries
will be fetched from cache if available.

The query runtime is optimized for the following types of queries:

- Grouping and counting queries, specifically counting observations/targets per
  condition per time interval.

These types of queries should execute in minutes for reasonable time windows and
numbers of source rows. It is acceptable for other types of queries to revert to
sequential scanning and execute in hours.


### Analysis Runtime

The analysis runtime runs analyses, executable binaries or scripts implementing
the analysis runtime interface, installed on one or more analysis nodes (which
need to have access to raw data and to the metadata and observation databases,
whether locally or via the network). It stores information about which files and
which observation sets have been analyzed by which analyzers, and information
about the analyzers themselves.

### Analysis Modules

*major change*
Analysis modules are invoked by the analysis runtime to generate observations.

There are two kinds of analysis modules:

- raw analysis modules, which take a raw measurement file and output
  observations.
- derived analysis modules, which take the observations in an observation set,
  Derived analysis modules can place their observations in one or multiple
  observation sets.

Analysis modules are added to the system by adding an appropriate row to the
metadata database. The information stored about each analysis module consists of
an executable path for the analyzer on the analysis host(s), a reference to a
source control repository and current commit reference or tag, and a display
name for the analyzer. These source control repositories have `bash` shell
scripts at well-known paths for installing and uninstalling analyzers, for
future automated deployment.


### Web Frontend

Allows access to all PAPI calls, and renders visualizations of query results.

### CLI PAPI client

Allows access to all PAPI calls.

## Interfaces

### Query Runtime (PAPI)

The interface allows submission of a query, cancellation of an identified query,
listing pending and running queries, and retrieving cached query results for
completed queries.

Details are given in [the Swagger API definition](papi.yaml). Query runtime
calls are available in subpaths of `/q` and `/qq`.

### Analysis Runtime (PAPI)

The analysis runtime interface allows its client to determine analyses
(analyzer/input pairs) that can be run, to submit an analysis to be run, and to
view the status of running analyses.

Details are given in [the Swagger API definition](papi.yaml). Analysis runtime
calls are available in subpaths of `/a` and `/aq`.

### Raw Data Submission, Access, Management (PAPI)

The raw data submission interface takes a metadata file and a data file via
POST, and stores the data on disk. Raw data files are associated with a
campaign.

The raw data access interface allows raw data to be downloaded. Raw data access
is generally limited to the original submitter/owner of the data.

The raw data management interface provides statistics for raw data files, and
allows raw data files to be removed, to provide for correction of errors or
handling of abuse of the raw data store.

All raw data operations are logged for auditing purposes.

Details are given in [the Swagger API definition](papi.yaml). Analysis runtime
calls are available in subpaths of `/r` and `/rd`.

### Access Control Administration (PAPI)

Creation and deletion of API keys happens via PAPI. API keys can have
one or more of the following permissions:

- raw data submission
- raw data management
- raw data access (on a per-campaign basis)
- observation set administration
- query submission
- cached query deletion
- query worker management
- analysis invocation
- analysis management
- analysis worker management
- access control administration

API keys have an expiration date, which can be changed. API keys have a display
name, which allows administrators to identify the owner/role of the key.

There is an administrative initialization command-line utility, which creates a user with access control administration rights.

Details are given in [the Swagger API definition](papi.yaml). Access control
administrative calls are available in subpaths of `/aca`.

### Observation Set Review and Administration (PAPI)

The observation set administration interface allows human review of observation
`pending_review` observation sets, as well as the management of the state of all
observation sets (deletion of sets until state `permanent`, and deprecation of
`permanent` sets).

Details are given in [the Swagger API definition](papi.yaml). Analysis runtime
calls are available in subpaths of `/osa`

### Runtime Interaction

The query and analysis runtimes should either share workers or otherwise
coordinate scheduling, to ensure that the workload on the production database is
either read-heavy or write-heavy.

### Analysis Module / Runtime

Both raw and derived analysis modules can also be queried about their interest in a
particular data item.

Analysis modules are implemented as UNIX executables. Without flags, they read
appropriate input on standard input, and write appropriate output on standard
output, returning with a zero exit status if the analysis was successful, and
any nonzero exit status otherwise.

With the `--interest` flag, they express interest in files and/or observation
sets based on metadata. They read this metadata as a JSON object on standard
input, and return with exit status 0 if they are interested, 1 if not
interested, and any other nonzero exit status otherwise.

Raw analysis modules take files of a given type on standard input, and produce
observations as newline-delimited JSON, with each line containing one object
with the following properties:

- `time`: a 2-array of timestamps as unix epoch UTC seconds
- `path`: an array of strings representing path elements
- `condition`: a condition name as a string
- `value`: an optional value associated with the condition as an integer
- `set`: the ID of the observation set associated with the observation as an integer

Derived analysis modules take the same format on standard input, and produce it
on standard output, with the caveat that the value of the `set` property, if
present, is used to group observations into sets (i.e. all observations with the
same `set` value will appear in the same observation set); the chosen
observation set ID will not be honored.

