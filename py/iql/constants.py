DICT_BINOP_TO_OP = {
  "eq" : "=",
  "ne" : "!=",
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
  'union-ls' : True,
  'subtraction' : True
}

DICT_EXPECTED_TYPES = {
  'eq' : None,
  'lt' : None,
  'gt' : None,
  'le' : None,
  'ge' : None,
  'ne' : None,
  'add' : ['N','T'],
  'sub' : ['N','T'],
  'mul' : 'N',
  'div' : 'N',
  'or' : 'B',
  'and' : 'B'
}

DICT_RETURN_TYPES = {
  'eq' : 'B',
  'lt' : 'B',
  'gt' : 'B',
  'le' : 'B',
  'ge' : 'B',
  'ne' : 'B',
  'contains' : 'B',
  'add' : None,
  'sub' : None,
  'mul' : None,
  'div' : None,
  'time' : 'T',
  'year' : 'N',
  'month' : 'N',
  'day' : 'N',
  'hour' : 'N',
  'minute' : 'N',
  'second' : 'N',
  'exists' : 'B'
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
  'second' : True,
  'exists' : True,
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
