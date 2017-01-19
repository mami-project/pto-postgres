DROP VIEW IF EXISTS iql_minimal;
DROP TABLE IF EXISTS observation;
DROP TABLE IF EXISTS condition_tree;
DROP TABLE IF EXISTS observation_set;

CREATE TABLE observation_set (
  osid INT NOT NULL,
  toc INT NOT NULL,
  toi INT NOT NULL
);

CREATE UNIQUE INDEX idx_observation_set_unique_osid ON observation_set (osid);

CREATE TABLE condition_tree (
  cid INT NOT NULL,
  name VARCHAR(255),
  parent INT,
  full_name VARCHAR(1024) NOT NULL
);

CREATE UNIQUE INDEX idx_condition_tree_unique_cid ON condition_tree (cid);

CREATE TABLE observation (
  oid INT NOT NULL,
  full_path VARCHAR(255)[],
  time_from TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  time_to TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  val_n REAL,
  observation_set INT NOT NULL,
  condition INT NOT NULL
);

CREATE UNIQUE INDEX idx_observation_unique_oid ON observation (oid);

INSERT INTO condition_tree(cid, name, parent, full_name) 
 VALUES(0, 'ecn', NULL, 'ecn');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(1, 'connectivity', 0, 'ecn.connectivity');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(2, 'works', 1, 'ecn.connectivity.works');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(3, 'broken', 1, 'ecn.connectivity.broken');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(4, 'transient', 1, 'ecn.connectivity.transient');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(5, 'offline', 1, 'ecn.connectivity.offline');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(6, 'negotiation_attempt', 0, 'ecn.negotiation_attempt');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(7, 'succeeded', 6, 'ecn.negotiation_attempt.succeeded');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(8, 'failed', 6, 'ecn.negotiation_attempt.failed');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(9, 'ce', 0, 'ecn.ce');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(10, 'ect_zero', 0, 'ecn.ect_zero');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(11, 'ect_one', 0, 'ecn.ect_one');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(12, 'super', 1, 'ecn.connectivity.super');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(13, 'works', 12, 'ecn.connectivity.super.works');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(14, 'broken', 12, 'ecn.connectivity.super.broken');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(15, 'transient', 12, 'ecn.connectivity.super.transient');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(16, 'offline', 12, 'ecn.connectivity.super.offline');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(17, 'weird', 12, 'ecn.connectivity.super.weird');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(18, 'path_dependent', 0, 'ecn.path_dependent');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(19, 'weak', 18, 'ecn.path_dependent.weak');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(20, 'strong', 18, 'ecn.path_dependent.strong');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(21, 'strict', 18, 'ecn.path_dependent.strict');

INSERT INTO condition_tree(cid, name, paretn, full_name)
 VALUES(22, 'site_dependent', 1, 'ecn.site_dependent');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(23, 'weak', 22, 'ecn.path_dependent.weak');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(24, 'strong', 22, 'ecn.path_dependent.strong');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(25, 'strict', 22, 'ecn.path_dependent.strict');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(26, 'seen', 10, 'ecn.ect_zero.seen');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(27, 'seen', 11, 'ecn.ect_one.seen');

INSERT INTO condition_tree(cid, name, parent, full_name)
 VALUES(28, 'seen', 9, 'ecn.ce.seen');



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
