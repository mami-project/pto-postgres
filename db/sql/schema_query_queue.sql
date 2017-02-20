CREATE TABLE query_queue(
  -- id which is a sha1 hash of the query
  id VARCHAR(255) NOT NULL,

  -- the iql query as json
  iql JSONb NOT NULL,

  -- the translated query to execute by the workers
  sql_query TEXT NOT NULL,

  -- result as json, NULL if not yet ready
  result JSONb,

  -- state
  --  running / new / failed
  state VARCHAR(255) NOT NULL,

  -- start and stop time of when the query
  -- will be filled in by worker. NULL if no
  -- worker has yet looked at this
  start_time TIMESTAMP WITHOUT TIME ZONE,
  stop_time TIMESTAMP WITHOUT TIME ZONE,
  submit_time TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE UNIQUE INDEX idx_query_id ON query_queue (id);
