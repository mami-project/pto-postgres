-- Minimal schema for iql_minimal

DROP VIEW IF EXISTS iql_minimal;
DROP TABLE IF EXISTS observation;
DROP TABLE IF EXISTS condition_tree;
DROP TABLE IF EXISTS observation_set;

CREATE TABLE observation_set (
  osid BIGSERIAL NOT NULL,
  toc INT NOT NULL,
  toi INT NOT NULL
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
