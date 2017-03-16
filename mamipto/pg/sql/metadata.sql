--
-- PostgreSQL DDL for MAMI PTO metadatabase
-- Contains metadata for raw uploads, observation sets, analyzers, and queries
--


-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 
--                             CONDITIONS                                  --
-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 


-- Map condition IDs to condition names. Condition logic is client-side. This
-- table is filled in by the database creation logic from the condition
-- definition file. Must have the same content as the table with the same name
-- in the observation database, or things break.
CREATE TABLE condition (
  cid INT PRIMARY KEY,
  full_name VARCHAR(1024)
);


-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 
--                             ANALYZERS                                   --
-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 

CREATE TABLE analyzer (
    aid BIGSERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    repourl VARCHAR(255) NOT NULL,
    python_class VARCHAR(255) NOT NULL
)


-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 
--                         OBSERVATION SETS                                --
-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 

-- States of an observation set:
--   "unknown": an ObservationSetWriter is instantiated and may want to
--     resume writing but it's not clear that the observation ID it refers
--     to exists
--   "in progress": an analyser is currently appending to this observation set
--   "pending review": the analyzer is now done with this observation set,
--     doesn't call observe() any more; set is waiting to be vetted
--   "public": the observation set has been vetted and is now ready for
--     public consumption; only now is this available to IQL
--  "permanent" as a result of a query becoming permanent (can't delete, but
--    can deprecate); can delete data as long as it's not permanent, after
--    that, _cannot_ delete any more
--  "deprecated": a formerly published observation set has been found to be
--    wrong. Not avalilable for IQL
CREATE TYPE os_state AS ENUM (
  'unknown',        -- after initialisation, before checking
  'in_progress',    -- analyser currently writing to this observation set
  'pending_review', -- observation set waiting to be vetted, no more additions
  'public',         -- successfully vetted, can now be used in IQL queries
  'permanent',      -- observation set used in permanent IQL query, can't delete this
  'deprecated'      -- defective observation set, only there to enable repeatability
);

-- Observation table revisions. We use revisions instead of timestamps
-- because timestamps are unreliable for determining what the state
-- of an observation set was at a given time. (Time stamps are only
-- reliable when nothing ever goes wrong.)
CREATE TABLE observation_set_revision (
  revision BIGSERIAL NOT NULL PRIMARY KEY,
  -- This timestamp is purely for informational purposes
  created_on TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc') NOT NULL,
  -- For informational purposes only. Might be used to answer the question,
  -- "who created revision 123?"
  creator VARCHAR(255)
);

CREATE TABLE observation_set (
  osid BIGSERIAL NOT NULL PRIMARY KEY,
  -- Reference to the analyzer creating this observation set
  aid VARCHAR(255) NOT NULL,
  -- Contains the name of the measurement campaign, for analysers that take
  -- raw data. May contain additional information for other analysers, or
  -- may be NULL in these cases
  campaign VARCHAR(255),
  state os_state,
  -- Revision ID when this observation set was created
  roc BIGINT NOT NULL,
  -- Revision ID when this observation set first became visible (state public)
  rov BIGINT,
  -- Revision ID when this observation set became deprecated
  rod BIGINT,

  FOREIGN KEY(roc)
    REFERENCES observation_set_revision(revision),
  FOREIGN KEY(rov)
    REFERENCES observation_set_revision(revision),
  FOREIGN KEY(rod)
    REFERENCES observation_set_revision(revision),
  FOREIGN KEY(aid)
    REFERENCES analyzer(aid)
);

CREATE TABLE observation_set_dependencies (
  osid BIGINT NOT NULL,
  depends_on BIGINT NOT NULL,

  PRIMARY KEY(osid, depends_on),
  FOREIGN KEY(osid) REFERENCES observation_set(osid),
  FOREIGN KEY(depends_on) REFERENCES observation_set(osid)
);

CREATE TABLE observation_set_conditions (
    osid BIGINT NOT NULL,
    cid BIGINT NOT NULL,
    PRIMARY KEY(osid, cid)
    FOREIGN KEY(osid) REFERENCES observation_set(osid),
    FOREIGN KEY(cidn) REFERENCES condition(cid)

)

CREATE TABLE observation_set_metadata (
  osid BIGSERIAL NOT NULL,
  key VARCHAR(255),
  value VARCHAR(255),

  FOREIGN KEY(osid)
    REFERENCES observation_set (osid)
);

-- WORK POINTER

-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 
--                       RAW MEASUREMENT FILES                             --
-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 

-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 
--                           ANALYSIS LOG                                  --
-- -------------------------------------------------------------------------- 
-- -------------------------------------------------------------------------- 
CREATE TYPE analysis_state AS ENUM (
  'unknown'         -- analyzer has not been asked about its interest
  'not_interested'  -- analyzer has been asked but is not interested in this observation set
  'interested',     -- analyzer is interested in this observation set but has not run
  'analyzed'        -- analyzer has analyzed this observation set
);

CREATE TABLE raw_analysis_log (
    aid BIGINT NOT NULL,
    filesystem_path VARCHAR(2048) NOT NULL,
    state analysis_state,
    FOREIGN KEY(aid) REFERENCES analyzer(aid),
    FOREIGN KEY(filesystem_path) REFERENCES uploads(filesystem_path)
);

CREATE TABLE derived_analysis_log (
    aid BIGINT NOT NULL,
    osid BIGINT NOT NULL,
    state analysis_state,
    FOREIGN KEY(aid) REFERENCES analyzer(aid),
    FOREIGN KEY(osid) REFERENCES observation_set(osid)
);