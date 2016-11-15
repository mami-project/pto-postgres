-- pto-postgres schema

-- Note: Tables are generally read-only except for inserting new
--       data. 

-- drop tables if exist
DROP TABLE IF EXISTS OBS_SRC_OBS;
DROP TABLE IF EXISTS OBS_SRC_UPL;
DROP TABLE IF EXISTS OBSERVATION;
DROP TABLE IF EXISTS PATH_NODE;
DROP TABLE IF EXISTS NODE;
DROP TABLE IF EXISTS PATH;
DROP TABLE IF EXISTS ANALYZER;

-- create tables

-- An analyzer, currently just a name.
CREATE TABLE ANALYZER (
  ID INT NOT NULL,
  NAME VARCHAR(255) NOT NULL
);


-- A node, name refers to IP/Hostname
CREATE TABLE NODE (
  ID INT NOT NULL,
  NAME VARCHAR(255) NOT NULL
);


-- A path with certain fields denormalized
CREATE TABLE PATH (
  ID INT NOT NULL,
  FULL_PATH VARCHAR(2048) NOT NULL,  -- denorm: full path joined with -'
  SIP VARCHAR(255) NOT NULL,         -- denorm: startpoint
  DIP VARCHAR(255) NOT NULL          -- denorm: endpoint
);


-- Encodes which nodes belong to which paths
CREATE TABLE PATH_NODE (
  PATH_ID INT NOT NULL,             -- references PATH
  NODE_ID INT NOT NULL,             -- references NODE
  POS INT NOT NULL
);

-- An observation
CREATE TABLE OBSERVATION (
  ID INT NOT NULL,
  PATH_ID INT NOT NULL,             -- references PATH
  ANALYZER_ID INT NOT NULL,         -- references ANALYZER
  TIME_FROM TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  TIME_TO TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  CONDITION VARCHAR(255) NOT NULL,
  VAL_I INT,
  VAL_S VARCHAR(255)
);

-- Which observations are derived from which observations
CREATE TABLE OBS_SRC_OBS (
  OBS_ID INT NOT NULL,              -- references OBSERVATION
  SRC_OBS INT NOT NULL              -- references OBSERVATION
);


-- Which observations are derived from which uploads
CREATE TABLE OBS_SRC_UPL (
  OBS_ID INT NOT NULL,              -- references OBSERVATION
  SRC_UPL VARCHAR(255) NOT NULL     -- ObjectID of the upload entry in the mongo database.
);
