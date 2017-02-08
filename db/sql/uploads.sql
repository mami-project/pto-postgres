CREATE TABLE uploads (
  -- Identify uploads by hash
  file_hash VARCHAR(255),

  -- When the file was uploaded
  time_of_upload TIMESTAMP WITHOUT TIME ZONE NOT NULL,

  -- Measurement time window
  start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  stop_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,

  -- Additionally metadata provided with the upload
  metadata JSONb NOT NULL,

  -- Name of the uploader
  uploader VARCHAR(255),

  -- Name of upload campaign
  campaign VARCHAR(255) NOT NULL,

  -- path on file system (relative)
  filesystem_path VARCHAR(2048) NOT NULL,

  time_of_invalidation INTEGER
);

CREATE INDEX idx_uploads_file_hash
 ON uploads ( file_hash );

CREATE UNIQUE INDEX idx_unique_uploads_filesystem_path
 ON uploads ( filesystem_path );

-- No need for other indexes so far as table contains
-- a lousy 4k documnets.
