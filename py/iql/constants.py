DICT_BINOP_TO_OP = {
  "eq" : "=",
  "lt" : "<",
  "gt" : ">",
  "le" : "<=",
  "ge" : ">=",
  "add" : "+",
  "sub" : "-",
  "mul" : "*",
  "div" : "/",
}

DICT_QUERY_OPS = {
  'sieve' : True,
  'simple' : True,
  'intersection' : True,
  'union' : True,
  'subtraction' : True
}

DICT_EXPECTED_TYPES = {
  'eq' : None,
  'lt' : None,
  'gt' : None,
  'le' : None,
  'ge' : None,
  'add' : ['I','T'],
  'sub' : ['I','T'],
  'mul' : 'I',
  'div' : 'I',
}

DICT_RETURN_TYPES = {
  'eq' : 'B',
  'lt' : 'B',
  'gt' : 'B',
  'le' : 'B',
  'ge' : 'B',
  'contains' : 'B',
  'add' : None,
  'sub' : None,
  'mul' : None,
  'div' : None,
  'time' : 'T',
  'year' : 'I',
  'month' : 'I',
  'day' : 'I',
  'hour' : 'I',
  'minute' : 'I',
  'second' : 'I'
}

DICT_N_OPS = {
  'and' : True,
  'or' : True
}

DICT_UNI_OPS = {
  'time' : True,
  'year' : True,
  'year' : True,
  'month' : True,
  'day' : True,
  'hour' : True,
  'minute' : True,
  'second' : True
}

DICT_BIN_OPS = {
  "eq" : True,
  "lt" : True,
  "gt" : True,
  "le" : True,
  "ge" : True,
  "add" : True,
  "sub" : True,
  "div" : True,
  "mul" : True,
  "contains" : True,
}
