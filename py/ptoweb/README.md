# ptoweb

aka PAPI.

## Config

You need to point `PTO_PAPI_SETTINGS` to a configuration file (i.e. `settings.py`) which contains
the entries `DBNAME`, `USER` and `PASSWD` (tells ptoweb how to connect to your database) and `RAW_UPLOAD_FOLDER` which points
to where uploaded raw data shall be physically stored.

Additionally you need `PTO_PAPI_IQL_SETTINGS` which contains the entries `IQL_TABLE`, `IQL_ATTR_TYPES` (dict),
`IQL_MSMNT_TYPES` (dict) to configure how it should use IQL. 
