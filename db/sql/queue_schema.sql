DROP TABLE IF EXISTS query_queue;

CREATE TABLE query_queue(
  id VARCHAR(255) NOT NULL,
  iql TEXT NOT NULL,
  sql_query TEXT NOT NULL,
  result TEXT,
  state VARCHAR(255) NOT NULL,
  start_time TIMESTAMP WITHOUT TIME ZONE,
  stop_time TIMESTAMP WITHOUT TIME ZONE
);

CREATE UNIQUE INDEX idx_query_id ON query_queue (id);
