DROP TABLE IF EXISTS analyzer;

CREATE TABLE analyzer (
    aid BIGSERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    repourl VARCHAR(255) NOT NULL,
    python_class VARCHAR(255) NOT NULL
)

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