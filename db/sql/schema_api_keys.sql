CREATE TABLE api_keys (
  name VARCHAR(255) NOT NULL,
  key VARCHAR(255) NOT NULL,
  permissions VARCHAR(255) NOT NULL,

  PRIMARY KEY (name)
);
