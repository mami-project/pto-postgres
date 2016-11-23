DICT_EXPECTED_TYPES_ATTR = {
  'time_to' : 'T',
  'time_from' : 'T',
  'path_id' : 'N',
  'dip' : 'S',
  'sip' : 'S',
  'full_path' : 'S',
  'path_id' : 'N',
  'analyzer' : 'S',
  'path_nodes' : '*S',
  'oid' : 'N',
  'name' : 'S'
}

DICT_MSMNT_TYPES = {
  'ecn.connectivity' : 'S',
  'ecn.negotiated' : 'N',
  'ecn.site_dependent' : '*S',
  'ecn.path_dependent' : '*S'
}

ALL_SQL_ATTRS = ['time_to', 'time_from', 'time_to', 'name', 'path_id', 'full_path', 
                 'dip', 'sip', 'analyzer', 'val_s', 'val_i', 'path_nodes']
