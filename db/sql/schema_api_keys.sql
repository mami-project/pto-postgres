CREATE TABLE api_keys (
  -- Who owns this key?
  name VARCHAR(255) NOT NULL,

  -- The key
  key VARCHAR(255) NOT NULL,

  -- Permissions
  --  String of characters
  --   u := upload
  permissions VARCHAR(255) NOT NULL,

  -- primary key shall be the key
  PRIMARY KEY (key)
);

CREATE UNIQUE INDEX idx_unique_api_keys_name ON api_keys ( name );
