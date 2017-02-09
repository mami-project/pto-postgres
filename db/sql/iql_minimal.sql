-- Minimal schema for iql_minimal

DROP VIEW IF EXISTS iql_minimal;
DROP TABLE IF EXISTS observation;
DROP TABLE IF EXISTS condition_tree;
DROP TABLE IF EXISTS observation_set;
DROP TABLE IF EXISTS observation_set_metadata;

DROP TYPE IF EXISTS os_state;

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

CREATE TABLE observation_set (
  osid BIGSERIAL NOT NULL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  toc TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc') NOT NULL,
  state os_state,
  toi INT
);

CREATE TABLE observation_set_metadata (
  osid BIGSERIAL NOT NULL,
  key VARCHAR(255),
  value VARCHAR(255),

  FOREIGN KEY(osid)
    REFERENCES observation_set (osid)
);

CREATE UNIQUE INDEX idx_observation_set_unique_osid ON observation_set (osid);

CREATE TABLE condition_tree (
  cid SERIAL NOT NULL,
  name VARCHAR(255),
  parent INT,
  full_name VARCHAR(1024) NOT NULL
);

CREATE UNIQUE INDEX idx_condition_tree_unique_cid ON condition_tree (cid);

CREATE TABLE observation (
  oid BIGSERIAL NOT NULL,
  full_path VARCHAR(255)[],
  time_from TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  time_to TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  val_n REAL,
  observation_set BIGSERIAL NOT NULL,
  condition INT NOT NULL,

  FOREIGN KEY (observation_set)
   REFERENCES observation_set (osid),

  FOREIGN KEY (condition)
   REFERENCES condition_tree (cid)
);

CREATE UNIQUE INDEX idx_observation_unique_oid ON observation (oid);


CREATE VIEW iql_minimal AS
 SELECT o.oid AS oid, 
        o.full_path AS full_path, 
        o.time_from AS time_from,
        o.time_to AS time_to, 
        o.val_n AS val_n, 
        o.observation_set AS observation_set,
        os.toc AS toc,
        os.toi AS toi,
        c.full_name as name
 FROM observation o
 JOIN observation_set os
   ON o.observation_set = os.osid
 JOIN condition_tree c
   ON o.condition = c.cid;
