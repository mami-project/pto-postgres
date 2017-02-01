CREATE TABLE query_queue(
  ID VARCHAR(255) NOT NULL,
  IQL JSONB NOT NULL,
  SQL_QUERY TEXT NOT NULL,
  RESULT JSONB,
  STATE VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX idx_query_id ON query_queue (id);
