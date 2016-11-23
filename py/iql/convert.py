import iql.constants as C
import iql.util as U

class Config:

  def __init__(self, msmnt_types = {}, expected_types = {}, known_projections = {}, tbl_name = "iql_data", all_sql_attrs = None, nub = True):
    self.DICT_MSMNT_TYPES = msmnt_types
    self.DICT_EXPECTED_TYPES_ATTR = expected_types
    self.DICT_KNOWN_PROJECTIONS = known_projections
    self.TBL_NAME = tbl_name
    self.ALL_SQL_ATTRS = all_sql_attrs


class Context:

  def __init__(self, projection, attribute):
    self.projection = projection
    self.attribute = attribute

    self.DICT_MSMNT_TYPES = {}
    self.DICT_EXPECTED_TYPES_ATTR = {}
    self.DICT_KNOWN_PROJECTIONS = {}
    self.TBL_NAME = "iql_data"

    
    if self.projection == None:
      self.projection = ''

    if self.attribute == '':
      self.attribute = None

    self.msmnt_name = None

    self.limit = 128
    self.skip = 0
    self.order = None
    self.nub = False

  def config_from(self, config):
    self.DICT_MSMNT_TYPES = config.DICT_MSMNT_TYPES
    self.DICT_EXPECTED_TYPES_ATTR = config.DICT_EXPECTED_TYPES_ATTR
    self.DICT_KNOWN_PROJECTIONS = config.DICT_KNOWN_PROJECTIONS
    self.TBL_NAME = config.TBL_NAME
    self.ALL_SQL_ATTRS = config.ALL_SQL_ATTRS


def convert_simple(exp, context):
  """
  Converts a simple query to SQL.
  """

  (sql, return_type, a) = convert_exp(exp, 'l0', context)

  if return_type == '$':
    raise ValueError("Not a boolean expression: " + str(exp))

  if return_type != "B":
    raise ValueError("Expected type `B' but found `" + return_type + "': " + str(exp))

  if context.msmnt_name != None:
    sql_ = "l0.name = '" + context.msmnt_name + "' AND "
  else:
    sql_ = " "

  distinct = 'DISTINCT' if context.nub else ''

  if context.attribute == '' or context.attribute == None:
    return "SELECT * FROM " + context.TBL_NAME + " l0 WHERE " + sql_ + sql
  else:
    return ("SELECT %s %s(l0.%s) AS %s FROM %s l0 WHERE " % (distinct, context.projection, context.attribute, context.attribute, context.TBL_NAME)) + sql_ + sql



def convert_choice(operands, cur_table, context):
  """
  Moo
  """

  U.expect_array(operands, 0, "`choice'")

  if len(operands) < 2:
    raise ValueError("`choice' expects array of size 2: " + str(operands))

  if context.msmnt_name != None:
    raise ValueError("Can't use `choice' because expression is already bound to `" + context.msmnt_name + "': " + str(operands))

  choices = []

  for operand in operands:
    (sql, return_type, a) = convert_exp(operand, cur_table, context)

    if return_type != "B":
      raise ValueError("Expected type `B' but found `" + return_type + "': " + str(operand))

    if context.msmnt_name != None:
      sql = "%s.name = '%s' AND (%s)" % (cur_table, context.msmnt_name, sql)

    context.msmnt_name = None

    choices.append("(%s)" % sql)

  sql = " OR ".join(choices)

  return ("(%s)" % sql, "B", "")


def get_limit_clause(context):
  if context.skip <= 0:
    return " LIMIT %d " % context.limit
  else:
    return " LIMIT %d OFFSET %d " % (context.limit, context.skip)


def convert(query, config = Config()):
  """
  Converts a query to SQL.
  """

  

  context = Context('', '')

  context.config_from(config)

  # If there's an attribute or projection set we use them

  if 'settings' in query:
    settings = query['settings']
  
    if 'nub' in settings:
      context.nub = not(not(settings['nub']))
    else: context.nub = True

    if 'limit' in settings:
      U.expect_int(settings['limit'], "`settings.limit'")
      context.limit = settings['limit']

      if context.limit >= 500 or context.limit <= 0:
        context.limit = 500

      if 'skip' in settings:
        U.expect_int(settings['skip'], "`settings.skip'")
        context.skip = settings['skip']

    if 'projection' in settings:
      projection = settings['projection']

      if type(projection) == type(''):
        context.projection = projection
      else:
        raise ValueError("Invalid value for `settings.projection'. Need string: " + str(query))

      if not U.is_known_projection(context.projection, context):
        raise ValueError("Unknown projection `" + str(self.projection) + "': " + str(query))

    if 'attribute' in settings:
      context.attribute = U.resolve_attribute(settings['attribute'], context, "`attribute.settings'")

    if 'order' in settings:
      order = settings['order']

      U.expect_array(order, 2, "`settings.order'")

      attribute = order[0]
      asc_desc = order[1]

      attribute = U.resolve_attribute(attribute, context, "`settings.order'")

      if context.attribute != None and context.attribute != '':
        if context.attribute != attribute:
          raise ValueError("Can't order by `" + attribute + "': " + str(query))

      U.expect_one_of(asc_desc, ['asc','desc'], "`settings.order'")
      asc_desc = asc_desc.upper()

      context.order = (attribute, asc_desc)


  if not 'query' in query:
    raise ValueError("Missing `query': " + str(query))  

  query = query['query']

  if "all" in query:
    query = query['all']

    U.expect_array(query, 1, "`all'")

    query = query[0]
  
    sql_ = convert_query(query, context)

    sql = "SELECT * FROM (%s) z " % sql_

    if context.order != None:
      sql += "ORDER BY z.%s %s " % context.order

    sql += get_limit_clause(context)

    return sql

  elif "sieve" in query:
    query = query['sieve']

    U.expect_array(query, 0, "`sieve'")

    sql_ = convert_sieve(query, context, attributes = context.ALL_SQL_ATTRS)

    sql = "SELECT * FROM (%s) z " % sql_

    if context.order != None:
      sql += "ORDER BY z.(\"%s:0\") %s " % context.order

    sql += get_limit_clause(context)

    return sql

  elif "count" in query:
    query = query['count']

    U.expect_array(query, 0, "`count'")

    if len(query) == 1:
      query = query[0]

      sql_ = convert_query(query, context)

      sql = "SELECT COUNT(*) FROM (%s) z " % sql_

      if context.order != None:
        sql += "ORDER BY z.%s %s " % context.order

      sql += get_limit_clause(context)

      return sql; 
    
    elif len(query) >= 2:
      attribute = query[0]
      raw_attribute = attribute
      overwrite_order = False
      attributes = [attribute]

      if U.is_array(attribute):
        if len(attribute) >= 1:
          attributes = attribute
          attribute = attributes[-1]
          raw_attribute = attributes[-1]
        else:
          raise ValueError("`count.0' if array specified the array must not be empty:" + str(query))

      attributes = list(map(lambda a: "z.%s" % U.resolve_attribute(a, context, "`count.0.x'"), attributes))
     
      if len(query) == 3:
        order = query[2]
        overwrite_order = True
        if not order in ['asc','desc']:
          raise ValueError("`count.3' must be either `asc' or `desc'!")

      query = query[1]

      attribute = U.resolve_attribute(attribute, context, "`count.0'")

      if context.attribute != None:
        if context.attribute != attribute:
          raise ValueError("Can't count `" + attribute + "': " + str(query))

      if context.order != None:
        if not ("z."+context.order[0]) in attributes:
          raise ValueError("Can't order by `" + context.order[0] + "' due to `count': " + str(query))


      sql_ = convert_query(query, context)

      sql = "SELECT " + ",".join(attributes) + ", COUNT(z.%s) AS count FROM (%s) z WHERE z.%s IS NOT NULL\n" % (attribute, sql_, attribute)

      if raw_attribute.startswith("$"):
        raw_attribute = raw_attribute[1:]
        sql += "AND z.name = '%s' " % raw_attribute

      sql += "GROUP BY " + ",".join(attributes) + " "

      if context.order != None:
        if not overwrite_order:
          sql += "ORDER BY z.%s %s " % context.order
        else:
          sql += "ORDER BY z.count %s " % order
      else:
        if overwrite_order:
          sql += "ORDER BY z.count %s " % order

      sql += get_limit_clause(context)

      return sql; 

    else:
      raise ValueError("`count' expects array of size 1, 2 or 3: " + str(query))

  else:
    raise ValueError("Expected `count' or `all': " + str(query))



def convert_query(query, context):
  """
  Converts a query to SQL.
  """

  context.msmnt_name = None  

  if "sieve" in query:

    exps = query["sieve"]
    return convert_sieve(exps, context)

  elif "sieve-ex" in query:

    exps = query["sieve-ex"]
    return convert_sieve_ex(exps, context)

  elif "lookup" in query:
    return convert_lookup(query['lookup'], context)

  elif "nub" in query:
    query = query["nub"]
    U.expect_array(query, 1, "`nub'")

    return "(SELECT DISTINCT * FROM (%s))" % convert_query(query, context)

  elif "simple" in query:

    query = query["simple"]

    if type(query) == type([]):

      if len(query) != 1:
        raise ValueError("Error: `simple' expects Array of size 1: " + str(query))

      query = query[0]

    return convert_simple(query, context)

  elif "intersection" in query:

    subqueries = query["intersection"]
    return convert_set_op(subqueries, 'INTERSECT', context)

  elif "union" in query:

    subqueries = query["union"]
    return convert_set_op(subqueries, 'UNION', context)

  elif "union-ls" in query:
  
    subqueries = query['union-ls']
    return convert_set_op(subqueries, 'UNION ALL', context)

  elif "subtraction" in query:

    subqueries = query["subtraction"]
    return convert_set_op(subqueries, 'EXCEPT', context)

  else:
    raise ValueError("Need one of `sieve', `simple', `intersection', `union' or `subtraction': " + str(query))


def convert_lookup(arguments, context):

  U.expect_array(arguments, 0, "`lookup'")

  if len(arguments) < 3 or len(arguments) > 4:
    raise ValueError("`lookup' requires array of size 3 or 4: " + str(arguments))

  projection = arguments[0]
  attribute = arguments[1]
  query = arguments[2]

  if len(arguments) == 4:
    filter_ = arguments[3]
  else:
    filter_ = None

  U.expect_str(projection, "`lookup.0'")
  U.expect_str(attribute, "`lookup.1'")
  U.expect_object(query, "`lookup.2")

  attribute = U.resolve_attribute(attribute, context, "`lookup'")

  new_context = Context(projection, attribute)
  new_context.config_from(context)
  sql = convert_query(query, new_context)

  sql_filter = ""

  distinct = 'DISTINCT' if context.nub else ''

  if filter_ != None:
    new_context = Context('','')
    new_context.config_from(context)
    sql_filter = convert_exp(filter_, "W", new_context)
    if sql_filter[1] != "B":
      raise ValueError("`lookup.3' expects `B': " + str(filter_))

    sql_filter = " WHERE " + sql_filter[0] + " "

  if context.attribute == '' or context.attribute == None:
    sql = "(SELECT W.* FROM (%s) v JOIN %s w ON %s(w.%s) = (v.%s) %s)" % (sql, context.TBL_NAME, projection, attribute, attribute, sql_filter)
  else:
    sql = "(SELECT %s %s(W.%s) FROM (%s) v JOIN %s w ON %s(w.%s) = (v.%S) %s)" % (distinct, projection, attribute, sql, context.TBL_NAME, projection, attribute, attribute, sql_filter)

  return sql
  


def convert_set_op(queries, set_op, context):
  """
  Converts a set operation query to SQL.
  """  

  if context.attribute == '' or context.attribute == None:
    if not set_op.startswith("UNION "): raise ValueError("Set operations require `attribute': " + str(queries))

  if type(queries) != type([]):
      raise ValueError("Error: Expected Array but not found: " + str(exps))

  subqueries = []

  for query in queries:
    subqueries.append(convert_query(query, context))

  sql = "("
  i = 0
  while i < len(subqueries):
    sql += "(" + subqueries[i] + ") "

    if i != len(subqueries) - 1:
      sql += set_op + "\n "

    i += 1

  sql += ")"

  return sql


def convert_sieve_ex(exps, context):
  """
  Ex-Sieve
  """

  U.expect_array(exps, 0, "`sieve-ex'")

  if len(exps) < 3:
    raise ValueError("`sieve-ex' requires array of at least size 3: "  + str(exps))

  projection_function = exps[0]
  attribute = exps[1]

  U.expect_str(projection_function, "`sieve-ex.0'")
  U.expect_str(projection_function, "`sieve-ex.1'")

  if not U.is_known_projection(projection_function, context):
    raise ValueError("Unkown projection function `%s': %s" % (projection, str(exps)))

  attribute = U.resolve_attribute(attribute, context, "`sieve-ex.1'")

  exps = exps[2:]

  i = 0

  wheres = []

  for exp in exps:

    context.msmnt_name = None
    (sql, return_type, a) = convert_exp(exp, "l" + str(i), context)

    if return_type != "B":
      raise ValueError("Expected type `B' or boolean expression but found `" + return_type + "': " + str(exp))

    if context.msmnt_name != None:
      wheres.append("l" + str(i) + ".name = '" + context.msmnt_name + "'")

    wheres.append(sql)

    i += 1

  sql_unnests = []
  for sql_attribute in context.ALL_SQL_ATTRS:
    q = 0
    sqlb = "unnest(ARRAY[%s]) as %s"
    sqlbattrs = []
    while q < i:
      sqlbattrs.append("(l%d.%s)" % (q, sql_attribute))
      q += 1
    sqlb = sqlb % (",".join(sqlbattrs), sql_attribute)
    sql_unnests.append(sqlb)

  if context.attribute == '' or context.attribute == None:
    sql = "(SELECT %s FROM " % (',\n'.join(sql_unnests))
  else:
    distinct = 'DISTINCT' if context.nub else ''
    sql = "(SELECT %s %s(l0.%s) AS %s FROM\n" % (distinct, context.projection, context.attribute, context.attribute)

  sql += "%s l0 " % (context.TBL_NAME)
  j = 1

  while j < i:
    sql += "JOIN %s l%d " % (context.TBL_NAME, j)
    sql += "ON %s(l%d.%s) = %s(l%d.%s)\n" % (projection_function, j-1, attribute, projection_function, j, attribute)
    j += 1

  sql += "WHERE\n"
  
  j = 0

  i = len(wheres)

  while j < i:
    sql += wheres[j] + " "
    if(j != i - 1):
      sql += "AND\n"
    j += 1

  return sql + ")"
    
  return sql

def convert_sieve(exps, context, attributes = None):
  """
  Converts a sieve operation query to SQL.
  """

  if context.attribute == '' or context.attribute == None:
    raise ValueError("`sieve' requires `settings.attribute': " + str(exps))


  if type(exps) != type([]):
      raise ValueError("Error: Expected Array but not found: " + str(exps))

  i = 0

  wheres = []

  for exp in exps:

    context.msmnt_name = None
    (sql, return_type, a) = convert_exp(exp, "l" + str(i), context)

    if return_type != "B":
      raise ValueError("Expected type `B' or boolean expression but found `" + return_type + "': " + str(exp))

    if context.msmnt_name != None:
      wheres.append("l" + str(i) + ".name = '" + context.msmnt_name + "'")

    wheres.append(sql)

    i += 1

  distinct = 'DISTINCT' if context.nub else ''

  if attributes == None:
    sql = "(SELECT %s %s(l0.%s) AS %s FROM\n" % (distinct, context.projection, context.attribute, context.attribute)
  else:
    q = 0
    sql_attrs_selects = []
    while q < i:
      sql_attrs = ",".join(list(map(lambda a: "%s(l%d.%s) as \"%s:%d\"" % (context.projection if a == context.attribute else '',q,a,a,q), attributes)))
      sql_attrs_selects.append(sql_attrs)
      q += 1

    sql_attrs_select_line = ",".join(sql_attrs_selects)

    sql = "(SELECT %s FROM\n" % sql_attrs_select_line

  sql += "%s l0 " % (context.TBL_NAME)
  j = 1

  while j < i:
    sql += "JOIN %s l%d " % (context.TBL_NAME, j)
    sql += "ON %s(l%d.%s) = %s(l%d.%s)\n" % (context.projection, j-1, context.attribute, context.projection, j, context.attribute)
    j += 1

  sql += "WHERE\n"
  
  j = 0

  i = len(wheres)

  while j < i:
    sql += wheres[j] + " "
    if(j != i - 1):
      sql += "AND\n"
    j += 1

  return sql + ")"



def convert_exp(exp, cur_table, context):
  """
  Converts an expression to SQL.
  """

  if type(exp) == type({}):

    if len(exp) != 1:
      raise ValueError("Expected dictionary of size one: " + str(exp))

    operation = list(exp.keys())[0]

    return convert_operation(operation, exp[operation], cur_table, context)

  elif type(exp) == type(""):

    if not exp.startswith("$") and not exp.startswith("@"):
      return ("'" + exp + "'", "S", "")
    elif exp.startswith("$"):

      if context.msmnt_name == None:
        context.msmnt_name = exp[1:]
      else:
        if context.msmnt_name != exp[1:]:
          raise ValueError("Found `" + str(exp) + "' but expected `$" + context.msmnt_name + "'")

        
      exp = exp[1:]

      if not U.is_known_msmnt(exp, context):
        raise ValueError("Unknown measurement name `" + exp + "': " + str(exp))

      return ("$" + exp, "$", U.get_msmnt_type(exp, context))

    elif exp.startswith('@'):
      attr_name = U.get_attribute_name(exp)[1:]

      if not U.is_known_attribute(U.get_attribute_name(attr_name), context):
        raise ValueError("`" + exp + "' is unknown: " + str(exp))

      return (exp, U.get_data_type_for_attribute(attr_name, context), "")

  elif type(exp) == type(0):
    return (str(exp), "I", "")



def convert_operation(operation, operands, cur_table, context):
  """
  Converts operation to SQL
  """

  if operation == "choice":
    return convert_choice(operands, cur_table, context)

  elif U.is_n_op(operation):
    return convert_n_op(operation, operands, cur_table, context)

  elif U.is_bin_op(operation):
    if operation == 'contains':
      return convert_contains(operands, cur_table, context)

    return convert_bin_op(operation, operands, cur_table, context)

  elif U.is_uni_op(operation):
    return convert_uni_op(operation, operands, cur_table, context)

  elif U.is_query_op(operation):
    raise ValueError("`" + operation + "' is not allowed in expressions: " + str(operands))

  else:
    raise ValueError("Unknonw operation `" + operation + "': " + str(operands))



def convert_uni_op(operation, operands, cur_table, context):
  """
  Converts unary operations to SQL.
  """

  if len(operands) != 1:
    raise ValueError("Operation `" + operation + "' expects exactly one argument: " + str(operands))

  if operation == 'time':

    if type(operands[0]) != type(""):
      raise ValueError("Literal of type `S' expected: " + str(operands))

    return ("'" + operands[0] + "'", "T", "")

  elif operation in ['year','date','month','hour','minute','second']:
    return convert_date_part(operation, operands, cur_table, context)



def convert_date_part(operation, operands, cur_table, context):
  """
  Date functions
  """

  U.expect_array(operands, 1, "`%s'" % operation)

  operand = operands[0]

  (sql, data_type, cond_type) = convert_exp(operand, cur_table, context)

  if data_type == "$": data_type = cond_type

  if data_type != "T":
    raise ValueError("Expected `T' but found `%s' in `%s': %s" % (data_type, operation, str(operands)))

  return ("(date_part('%s',%s)::INT)" % (operation, to_sql_col_val(sql, cur_table, data_type)),"I","")




def convert_n_op(operation, operands, cur_table, context):
  """
  Converts n-ary operations to SQL.
  """

  exps = []

  expected_type = None
  
  for operand in operands:
    operand_ = convert_exp(operand, cur_table, context)
    (sql, data_type, cond_data_type) = operand_

    if data_type != "B":
      raise ValueError("Expected `B' but found `" + data_type + "': " + str(operands))

    exps.append(operand_)

  sql = "("
  i = 0

  while i < len(exps):
    sql += exps[i][0]

    if i != (len(exps) - 1):
      sql += " " + operation.lower() + " "

    i += 1

  sql += ")"

  return (sql, "B", "")



def to_sql_col_val(value, cur_table, data_type = ''):
  """
  Converts value to SQL.
  """

  if value.startswith("@"): 

    if not ":" in value[1:]: 
      return cur_table + "." + value[1:]

    value = value[1:]
    parts = value.split(":")

    if len(parts) != 2:
      raise ValueError("Illegal reference `" + value + "'.")

    return "l" + str(parts[1]) + "." + parts[0]

  elif value.startswith("$"):

    if not ":" in value[1:]:
      return cur_table + "." + "VAL_" + data_type

    value = value[1:]
    parts = value.split(":")
    
    if len(parts) != 2:
      raise ValueError("Illegal reference `" + value + "'.")

    return "l" + str(parts[1]) + ".VAL_"

  return value



def convert_contains(operands, cur_table, context):
  """
  Convert contains operation
  """

  U.expect_array(operands, 2, "`contains'")

  (sql_0, data_type_0, cond_type_0) = convert_exp(operands[0], cur_table, context)
  if data_type_0 == "$": data_type_0 = cond_type_0

  (sql_1, data_type_1, cond_type_1) = convert_exp(operands[1], cur_table, context)
  if data_type_1 == "$": data_type_1 = cond_type_1

  if not data_type_0.startswith("*"):
    raise ValueError("`contains.0' must be of type *a: " + str(operands))

  if not data_type_1 == data_type_0[1:]:
    raise ValueError("`%s' is incompatible with `%s' for `contains': %s" % (data_type_1, data_type_0, str(operands)))

  if data_type_0 == '*S':
    return ("(%s @> ARRAY[%s]::VARCHAR[])" % (to_sql_col_val(sql_0, cur_table, data_type_0), to_sql_col_val(sql_1, cur_table, data_type_1)), "B", "")
  elif data_type_0 == '*I':
    return ("(%s @> ARRAY[%s]::INT[])" % (to_sql_col_val(sql_0, cur_table, data_type_0), to_sql_col_val(sql_1, cur_table, data_type_1)), "B", "")
  else:
    raise ValueError("Unsupported type `%s': %s" % (data_type_0, str(operands)))



def convert_bin_op(operation, operands, cur_table, context):
  """
  Converts binary operations to SQL.
  """

  if len(operands) != 2:
    raise ValueError("Operation `" + operation + "' expects exactly two arguments: " + str(operands))

  exps = []

  operator = U.get_operator(operation)
  expected_type = U.get_expected_types(operation)

  #  Expected type is a string containing the types the operation accepts.
  #  If the expected type is none then the type of the first argument becomes
  #  the expected type. If the return type is None then the return type is set to
  #  the expected type. If an operation accepts multiple types then the return type
  #  of the first argument is checked and the expected type is narrowed down to the
  #  type of the first argument.
  
  for operand in operands:
    operand_ = convert_exp(operand, cur_table, context)
    (sql, data_type, cond_data_type) = operand_

    # The '$' indicates that we need to treat this one differently later on.
    if data_type == '$': 
      data_type = cond_data_type

    if expected_type == None:
      expected_type = data_type
    else:
      if data_type not in expected_type:
        raise ValueError("Expected type `" + expected_type + "' but found `" + data_type + "': " + str(operand))
      else:
        expected_type = data_type

    exps.append(operand_)

  return_type = U.get_return_type(operation)

  if return_type == None:
    return_type = expected_type

  # On '$' we need to use one of the VAL_ columns and the third element in the tuple tells us
  # what the type of the measurement actually is.

  if exps[0][1] == "$" and exps[1][1] == "$":
    # This should never happen because this is checked earlier but just in case
    # we messed something up maybe this helps us detecting that we messed up.
    raise ValueError("Impossibru :(")

  elif exps[0][1] == "$":
    # Left argument is a measurement value

    sql = "(" + to_sql_col_val(exps[0][0], cur_table) + exps[0][2] + " " + operator + " " + to_sql_col_val(exps[1][0], cur_table) + ")"
    return (sql, return_type, "")

  elif exps[1][1] == "$":
    # Right argument is a measurement value

    sql = "(" + to_sql_col_val(exps[0][0], cur_table) + " " + operator + " " + to_sql_col_val(exps[1][0]) + exps[1][2] + ")"
    return (sql, return_type, "")

  else:
    # Both arguments are regular expressions.

    sql = "(" + to_sql_col_val(exps[0][0], cur_table) + " " + operator + " " + to_sql_col_val(exps[1][0], cur_table) + ")"
    return (sql, return_type, "")

