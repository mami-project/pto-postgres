# Path Transparency Observatory Component and Interface Definitions

The Path Transparency Observatory consists of several notional components: a raw measurement and database storage backend, a query runtime, an analysis runtime, a set of analysis modules, and a web frontend. This document describes the responsibilities of these components, and the interfaces among them. 

## Components

### Raw Measurement Data Storage and Metadata Database

### Observation Database(s)

### Query Runtime

note the query runtime also has a database for storing query metadata.

### Analysis Runtime

note the analysis runtime also has a database for storing analysis metadata.

### Analysis Modules

### Web Frontend

## Interfaces

### Query Runtime (PAPI)

The query runtime runs queries submitted in IQL over PAPI.

### Analysis Runtime (PAPI)

The analysis runtime runs analyses, executable binaries or scripts implementing the analysis runtime interface, installed on one or more analysis nodes (which need to have access to raw data and to the metadata and observation databases, whether locally or via the network). 

### Raw Data Submission (PAPI)

The raw data submission interface takes a metadata file and a data file via POST, and stores the data on disk.

### Administration

*change* Creation and deletion of API keys happens on the command line or through PAPI, to be determined. API keys
can have one or more of the following permissions:

- raw data submission
- raw data management
- query submission
- cached query deletion
- query worker management
- analysis invocation
- analysis management
- analysis worker management

API keys have an expiration date, which can be changed.
API keys have a display name, which 

### Runtime Interaction

note the query and analysis runtimes should either share workers or otherwise
coordinate scheduling, to ensure that the workload on the production database is
either read-heavy or write-heavy.

### Analysis Module / Runtime

There are two kinds of analysis modules:

- raw analysis modules, which take a raw measurement file of an appropriate
  type, and output observations as newline-delimited JSON.
- derived analysis modules, which take the observations in an observation set as
  newline-delimited JSON, and return new observations as newline-delimited JSON.
  Derived analysis modules can group observations into observation sets by
  assigning arbitrary values to their output observation sets; these will be
  rewritten by the runtime.

Both kinds of analysis module can also be queried about their interest in a
particular data item.

Analysis modules are implemented as UNIX executables. Without flags, they read
appropriate input on standard input, and write appropriate output on standard
output, returning with a zero exit status if the analysis was successful, and
any nonzero exit status otherwise. With the `-i` flag, they express interest
read metadata as a JSON object on standard input, and return with exit status 0
if they are interested, 1 if not interested, and any other nonzero exit status
otherwise.

