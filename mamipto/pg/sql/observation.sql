--
-- PostgreSQL DDL for MAMI PTO adatabase
-- Contains observation data. Links to the metadatabase via observation set ID.
--

-- Map condition IDs to condition names. Condition logic is client-side. This
-- table is filled in by the database creation logic from the condition
-- definition file. Must have the same content as the table with the same name
-- in the metadata database, or things break.
CREATE TABLE condition (
  cid INT PRIMARY KEY,
  full_name VARCHAR(1024)
);


--
-- Observation. Time / path / condition / (optional) value tuple. References condition by 
-- 
CREATE TABLE observation (
  oid BIGSERIAL NOT NULL,
  full_path VARCHAR(255)[],  -- array of path elements. 
                             -- possibly normalize this to a path element table
                             -- in a future revision.
  time_from TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  time_to TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  observation_set BIGINT NOT NULL, -- foreign reference to the observation set 
                                   -- metadata in the metadata database.
                                   -- joins have to happen on the client side
                                   -- here.
  condition INT NOT NULL,
  val_n INT,

  FOREIGN KEY (condition)
    REFERENCES condition (cid)
);