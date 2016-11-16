DICT_BINOP_TO_OP = {
  "eq" : "=",
  "lt" : "<",
  "gt" : ">",
  "le" : "<=",
  "ge" : ">=",
  "add" : "+",
  "sub" : "-",
  "mul" : "*",
  "div" : "/"
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
  'add' : 'IT',
  'sub' : 'IT',
  'mul' : 'I',
  'div' : 'I',
}

DICT_RETURN_TYPES = {
  'eq' : 'B',
  'lt' : 'B',
  'gt' : 'B',
  'le' : 'B',
  'ge' : 'B',
  'add' : None,
  'sub' : None,
  'mul' : None,
  'div' : None
}

DICT_N_OPS = {
  'and' : True,
  'or' : True
}

DICT_UNI_OPS = {
  'time' : True
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
  "mul" : True
}
