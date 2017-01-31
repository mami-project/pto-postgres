CREATE TABLE observation_fixed (
  oid  SERIAL  NOT NULL,
  full_path VARCHAR(255)[] NOT NULL,
  time_from TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  time_to TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  val_n REAL,
  observation_set INTEGER NOT NULL,
  name VARCHAR(255) NOT NULL,
  metadata JSONB,
  time_of_creation INTEGER NOT NULL,
  time_of_invalidation INTEGER NOT NULL,
  analyzer VARCHAR(255) NOT NULL
);
