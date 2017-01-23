class DefaultConfig:
  DEBUG = True
  TESTING = True
  DBNAME = 'pto_munt'
  USER = 'munt'
  PASSWD = 'test'

  IQL_TABLE='iql_minimal'
  
  IQL_ATTR_TYPES = {
      'time_to' : 'T',
      'time_from' : 'T',
      'full_path' : '*S',
      'name' : 'S',
      'observation_set' : 'N'
  }

  IQL_MSMNT_TYPES = {
      'ecn.connectivity' : 'S',
      'ecn.negotiated' : 'N',
  }