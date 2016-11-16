import iql.constants as C

def is_uni_op(operation):
  """
  Returns true if the operation is a unary one.
  False otherwise.
  """
  
  return operation in C.DICT_UNI_OPS



def is_bin_op(operation):
  """
  Returns true if the operation is a binary one.
  False otherwise.
  """
  
  return operation in C.DICT_BIN_OPS



def is_n_op(operation):
  """
  Returns true if the operation is a n-ary one.
  False otherwise.
  """
  
  return operation in C.DICT_N_OPS

def get_operator(operation):
  """
  Translates operation to an SQL operator.
  """
  
  return C.DICT_BINOP_TO_OP[operation]



def get_expected_types(operation):
  """
  Returns the types the operation expects.
  Returns None if no specific types are expected.
  """
  
  return C.DICT_EXPECTED_TYPES[operation]



def get_data_type_for_attribute(attribute):
  """
  Returns the data type for an attribute. 
  """  

  return context.DICT_EXPECTED_TYPES_ATTR[attribute]



def get_return_type(operation):
  """
  Returns the return type of an operation.
  Returns None when the return type of an operation should be set
  to it's expected types.
  """  

  return C.DICT_RETURN_TYPES[operation]



def is_query_op(operation):
  """
  Returns true if it is a query operation.
  False otherwise
  """  

  return operation in C.DICT_QUERY_OPS



def get_attribute_name(attribute):
  """
  Returns the name of an attribute.
  """

  if ":" in attribute:

    parts = attribute.split(":")
    return parts[0].lower()

  else: return attribute.lower()



def is_known_attribute(attribute, context):
  """
  Returns true if the attribute is known.
  """

  return attribute in context.DICT_EXPECTED_TYPES_ATTR



def get_msmnt_type(msmnt_name, context):
  """
  Returns the type of a measurement.
  """

  return context.DICT_MSMNT_TYPES[msmnt_name]



def is_known_msmnt(msmnt_name, context):
  """
  Returns true if the measurement is known.
  """

  return msmnt_name in context.DICT_MSMNT_TYPES



def is_known_projection(proj, context):
  """
  Returns true if the projection is known.
  """

  if proj == '':
    return True

  return proj in context.DICT_KNOWN_PROJECTIONS



def is_str(a):
  return type(a) == type('')



def is_array(a):
  return type(a) == type([])



def is_object(a):
  return type(a) == type({})



def expect_object(a, data):
  if not is_object(a):
    raise ValueError("`" + str(a) + "' is not an object: " + str(data))



def expect_str(a, data = 'n/a'):
  if not is_str(a):
    raise ValueError("`" + str(a) + "' is not a string: " + str(data))



def expect_array(a, size = 0, data  = 'n/a'):
  if not is_array(a):
    raise ValueError("`" + str(a) + "' is not an array: " + str(data))


  if size != 0:
    if len(a) != size:
      raise ValueError("Expected array of size " + str(size) + " but found array of size " + str(len(a)) + ": " + str(data))



def expect_one_of(a, xs, data = 'n/a'):
  if not a in xs:
    raise ValueError("Expected one of " + str(xs) + " but found `" + str(a) + "': " + data)



def split_s_exp(a, data):
  expect_object(a)

  if len(a) != 1:
    raise ValueError("Illegal S-Exp `" + str(a) + "': " + str(data))

  key = a.keys()[0]
  return (key, a[key])



def resolve_attribute(attribute, context, data):
  expect_str(attribute, data)

  attribute = attribute.lower()

  if attribute.startswith("$"):
    attribute = attribute[1:]

    if not is_known_msmnt(attribute, context):
      raise ValueError("Unkown measurement name `" + attribute + "': " + str(data))

    attribute = "val_" + get_msmnt_type(attribute).lower()

    return attribute

  elif attribute.startswith("@"):
    attribute = attribute[1:]

    if not is_known_attribute(attribute, context):
      raise ValueError("Unknown attribute `" + attribute + "': " + str(data))

    return attribute

  raise ValueError("$ or @ prefix required for `" + attribute + "': " + str(data))
