import iql.constants as C
import iql.util as U
from pg import escape_string

class Config:

  def __init__(self, msmnt_types = {}, expected_types = {}, known_projections = {}, tbl_name = "iql_data", all_sql_attrs = None, max_limit = 128):
    """
    Creates configuration containing necessary metadata for IQL to convert queries.

    Parameters:
      - msmnt_types : Dictionary with name of measurements as keys and the type of the measurement values as values.
      - expected_types : Dictionary with name of attributes as keys and the type of the attributes as values.
      - known_projections: Dictionary with name of projection functions as keys and the type of projections as values.
      - tbl_name : Name of the SQL table (or view).
      - all_sql_attrs : A list of string containing the names of all sql attributes. OPTIONAL. Defaults to None.
                        Required if sieve (aggregation) is to be supported.
      - max_limit : The upper limit of number of results to return. <=0 for no limit. Defaults to 128

    Notes:
      - Name of attributes, name of projection functions and tbl_name are restricted to
        [a-z][A-Z]_
      - An attribute, may not have any of the following names:
         count, average, max, min

    Example usage:
      import iql.convert as iqlc
      cfg = iqlc.Config(msmnt_types = {}, expected_types = {"test":"N", "observation_set" : "N"}, tbl_name = "iql_data")
      query = {"settings":{"filter":{"contains":[{"array":[1,2,3]},"@observation_set"]}},"query":{"all":[{"simple":[True]}]}}
      print(query)
      print(iqlc.convert(query, cfg))
    """

    U.expect_int(max_limit, "Config: max_limit")
    U.check_names_and_types(msmnt_types, "Config: msmnt_types")
    U.check_names_and_types(expected_types, "Config: expected_types", ['count','average','max','min'])
    U.check_names_and_types(known_projections, "Config: known_projections")

    self.DICT_MSMNT_TYPES = msmnt_types
    self.DICT_EXPECTED_TYPES_ATTR = expected_types
    self.DICT_KNOWN_PROJECTIONS = known_projections
    self.TBL_NAME = tbl_name
    self.ALL_SQL_ATTRS = all_sql_attrs
    self.MAX_LIMIT = max_limit

class Context:

  def __init__(self, projection, attribute):
    self.projection = projection
    self.attribute = attribute
    
    if self.projection == None:
      self.projection = ''

    if self.attribute == '':
      self.attribute = None

    self.msmnt_name = None

    self.limit = 128
    self.skip = 0
    self.order = None
    self.nub = True


  def copy_from(self, other_context):
    """
    Read config and nub, inner_select from a different context.
    This is merely a quirk to support `lookup`. Invokes `config_from`
    """

    self.config_from(other_context)
    self.nub = other_context.nub


  def config_from(self, config):
    """
    Load config from either Configuration or another context. Is also invoked by
    `copy_from`.
    """

    self.DICT_MSMNT_TYPES = config.DICT_MSMNT_TYPES
    self.DICT_EXPECTED_TYPES_ATTR = config.DICT_EXPECTED_TYPES_ATTR
    self.DICT_KNOWN_PROJECTIONS = config.DICT_KNOWN_PROJECTIONS
    self.TBL_NAME = config.TBL_NAME
    self.ALL_SQL_ATTRS = config.ALL_SQL_ATTRS
    self.MAX_LIMIT = config.MAX_LIMIT



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
  An experimental undocumented operation. 
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
  """
  Returns the LIMIT _ OFFSET _ clause for queries based on the information
  provided in the context.
  """

  if context.limit <= 0:
    if context.MAX_LIMIT <= 0:
      return " "
    else:
      context.limit = context.MAX_LIMIT

  if context.limit > context.MAX_LIMIT:
    context.limit = context.MAX_LIMIT

  if context.skip >= context.limit:
    context.skip = context.limit - 1

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

  view = ""

  if 'settings' in query:
    settings = query['settings']

    if 'filter' in settings:
      new_context = Context('', '')
      new_context.copy_from(context)
      (filter_sql, data_type, msmnt_type) = convert_exp(settings['filter'], context.TBL_NAME, new_context)

      if data_type == '$':
        raise ValueError("`settings.filter` can't reference measuremnt values!")

      if new_context.msmnt_name != None:
        raise ValueError("`settings.filter` can't reference measurement values!")

      view = "WITH %s AS (SELECT * FROM %s WHERE %s)\n" % (context.TBL_NAME + "__iql__", context.TBL_NAME, filter_sql)
      context.TBL_NAME += "__iql__"
  
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

  return view + convert_aggregation(query, context)


def convert_aggregation(query, context):
  """
  Converts one of the top-level 'aggregations' all, count, sieve, count-distinct.
  """

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

    if(context.ALL_SQL_ATTRS == None):
      raise ValueError("`sieve` (aggregation) is not supported with this configuration!")

    sql_ = convert_sieve(query, context, attributes = context.ALL_SQL_ATTRS)

    sql = "SELECT * FROM (%s) z " % sql_

    if context.order != None:
      sql += "ORDER BY z.(\"%s:0\") %s " % context.order

    sql += get_limit_clause(context)

    return sql

  elif ("count" in query) or ("count-distinct" in query):
    if "count" in query:
      query = query['count']
      distinct = False
    elif "count-distinct" in query:
      query = query['count-distinct']
      distinct = True

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

      if not distinct:
        sql = "SELECT " + ",".join(attributes) + ", COUNT(z.%s) AS count FROM (%s) z\n" % (attribute, sql_)
      else:
        select_attributes = attributes[:-1]
        if(len(select_attributes) > 0):
          sql = "SELECT " + ",".join(select_attributes) + ", COUNT(DISTINCT z.%s) AS count FROM (%s) z\n" % (attribute, sql_)
        else:
          sql = "SELECT COUNT(DISTINCT z.%s) AS count FROM (%s) z\n" % (attribute, sql_)

      if raw_attribute.startswith("$"):
        raw_attribute = raw_attribute[1:]
        sql += "WHERE z.name = '%s' " % raw_attribute

      if not distinct:
        sql += "GROUP BY " + ",".join(attributes) + " "
      else:
        group_attributes = attributes[:-1]
        if(len(group_attributes) > 0):
          sql += "GROUP BY " + ",".join(group_attributes) + " "

      if context.order != None:
        if not overwrite_order:
          sql += "ORDER BY z.%s %s " % context.order
        else:
          sql += "ORDER BY count %s " % order
      else:
        if overwrite_order:
          sql += "ORDER BY count %s " % order

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
  """
  Converts a lookup operation.
  """

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
  new_context.copy_from(context)
  sql = convert_query(query, new_context)

  sql_filter = ""

  distinct = 'DISTINCT' if context.nub else ''

  if filter_ != None:
    new_context = Context('','')
    new_context.copy_from(context)
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

  if len(queries) < 1:
    raise ValueError("Set operations require at least one argument!")

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
  Converts an extended sieve operation.
  """

  U.expect_array(exps, 0, "`sieve-ex'")

  if len(exps) < 3:
    raise ValueError("`sieve-ex' requires array of at least size 3: "  + str(exps))

  projection_function = exps[0]
  attribute = exps[1]

  U.expect_str(projection_function, "`sieve-ex.0'")
  U.expect_str(projection_function, "`sieve-ex.1'")

  if not U.is_known_projection(projection_function, context):
    raise ValueError("Unknown projection function `%s': %s" % (projection, str(exps)))

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
  for sql_attribute in ['oid']: # only unnest oid (bugfix)
    q = 0
    sqlb = "unnest(ARRAY[%s]) as %s"
    sqlbattrs = []
    while q < i:
      sqlbattrs.append("(l%d.%s)" % (q, sql_attribute))
      q += 1
    sqlb = sqlb % (",".join(sqlbattrs), sql_attribute)
    sql_unnests.append(sqlb)

  distinct = 'DISTINCT' if context.nub else ''

  if context.attribute == '' or context.attribute == None:
    sql = "(SELECT %s %s FROM " % (distinct, ',\n'.join(sql_unnests))
  else:
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

  sql = sql + ")"

  if context.attribute == '' or context.attribute == None: #need to back join (bugfix)
    print('moo')
    sql_ = "(SELECT T.* FROM (%s) F JOIN %s T ON F.oid = T.oid)" % (sql, context.TBL_NAME)
    sql = sql_
    
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
  Converts an expression to SQL. Return type is (exp AS sql, type, msmnt_type).
  """

  if type(exp) == type({}):

    if len(exp) != 1:
      raise ValueError("Expected dictionary of size one: " + str(exp))

    operation = list(exp.keys())[0]

    return convert_operation(operation, exp[operation], cur_table, context)

  elif type(exp) == type(""):

    if not exp.startswith("$") and not exp.startswith("@"):
      return ("'" + escape_string(exp) + "'", "S", "")
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

  elif U.is_num(exp):
    return (str(exp), "N", "")

  elif U.is_bool(exp):
    if exp: 
      return ('(TRUE)',"B", "")
    else:
      return ('(FALSE)',"B","")

  raise ValueError("ORLY? %s" % str(exp))



def convert_operation(operation, operands, cur_table, context):
  """
  Converts operation to SQL
  """

  if operation == "choice":
    return convert_choice(operands, cur_table, context)
  elif operation == "array":
    return convert_array(operands, cur_table, context)

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
    raise ValueError("Unknown operation `" + operation + "': " + str(operands))



def convert_uni_op(operation, operands, cur_table, context):
  """
  Converts unary operations to SQL.
  """

  if len(operands) != 1:
    raise ValueError("Operation `" + operation + "' expects exactly one argument: " + str(operands))

  if operation == 'time':

    if(U.is_str(operands[0])):
      dt = datetime.datetime.strptime(operands[0],'%Y-%m-%d %H:%M:%S')

      return ("('" + operands[0] + "'::TIMESTAMP WITHOUT TIME ZONE)", "T", "")
    elif(U.is_num(operands[0])):
      return ("(to_timestamp(%d)::TIMESTAMP WITHOUT TIME ZONE)" % operands[0], "T", "")
    else:
      raise ValueError("`time' expects literal of type `N' or `S': " + str(operands))

  elif operation == 'exists':

    U.expect_str(operands[0])

    if not U.is_known_msmnt(operands[0], context):
      raise ValueError("Unknown measurement name: " + str(operands[0]))

    context.msmnt_name = operands[0]

    return ("(%s.name = '%s')" % (cur_table, operands[0]), "B", "")

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

  return ("(date_part('%s',%s)::REAL)" % (operation, to_sql_col_val(sql, cur_table, data_type)),"N","")



def convert_array(operands, cur_table, context):
  """
  Convert array.
  """

  # Currently is tailored to support arrays of strings or numbers
  # but not nested arrays.

  U.expect_array(operands, 0, "`array'")

  values = []
  expected_type = None

  for operand in operands:
    (sql, data_type, cond_data_type) = convert_exp(operand, cur_table, context)

    if data_type == '$': data_type = cond_data_type

    if expected_type != None:
      if data_type != expected_type:
        raise ValueError("Expected type `%s' but found `%s': %s" % (expected_type, data_type, str(operand)))
    else:
      expected_type = data_type

    values.append(sql)

  if expected_type not in ['S','N']:
    raise ValueError("Currently only `*S' and `*N' are supported: %s" % str(operands))

  if expected_type == 'S':
    return ("(ARRAY[%s]::VARCHAR[])" % (",".join(values)), "*S", "")
  elif expected_type == 'N':
    return ("(ARRAY[%s]::REAL[])" % (",".join(values)), "*N", "")



def convert_n_op(operation, operands, cur_table, context):
  """
  Converts n-ary operations to SQL.
  """

  # Currently is tailored to support or/and 

  exps = []

  expected_type = U.get_expected_types(operation)

  if len(operands) < 1:
    raise ValueError("`%s' needs at least one argument!" % operation)
  
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

  # Map human-readable type representation to name part in SQL
  if data_type == '*S':
    data_type = 'A_S'
  elif data_type == '*N':
    data_type = 'A_N'

  # Attribute reference
  if value.startswith("@"):

    if not ":" in value[1:]: 
      return cur_table + "." + value[1:]

    value = value[1:]
    parts = value.split(":")

    if len(parts) != 2:
      raise ValueError("Illegal reference `" + value + "'.")

    return "l" + str(parts[1]) + "." + parts[0]

  # Value reference
  elif value.startswith("$"):

    if not ":" in value[1:]:
      return cur_table + "." + "VAL_" + data_type

    value = value[1:]
    parts = value.split(":")
    
    if len(parts) != 2:
      raise ValueError("Illegal reference `" + value + "'.")

    return "l" + str(parts[1]) + ".VAL_"


  # Verbatim
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
  elif data_type_0 == '*N':
    return ("(%s @> ARRAY[%s]::REAL[])" % (to_sql_col_val(sql_0, cur_table, data_type_0), to_sql_col_val(sql_1, cur_table, data_type_1)), "B", "")
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
      if U.is_array(expected_type) and (data_type not in expected_type):
        raise ValueError("Unexpected type `%s' for `%s': %s" % (data_type, operation, str(operand)))
      elif U.is_array(expected_type) and (data_type in expected_type):
        expected_type = data_type
      elif expected_type != data_type:
         raise ValueError("Expected type `" + expected_type + "' but found `" + data_type + "': " + str(operand))

    exps.append(operand_)

  return_type = U.get_return_type(operation)

  if return_type == None:
    return_type = expected_type

  # On '$' we need to use one of the VAL_ columns and the third element in the tuple tells us
  # what the type of the measurement actually is.

  if exps[0][1] == "$" and exps[1][1] == "$":
    sql = "(" + to_sql_col_val(exps[0][0], cur_table, expected_type) + " " + operator + " " + to_sql_col_val(exps[1][0], cur_table, expected_type) + ")"
    return (sql, return_type, "")

  elif exps[0][1] == "$":
    # Left argument is a measurement value

    sql = "(" + to_sql_col_val(exps[0][0], cur_table, expected_type)  + " " + operator + " " + to_sql_col_val(exps[1][0], cur_table) + ")"
    return (sql, return_type, "")

  elif exps[1][1] == "$":
    # Right argument is a measurement value

    sql = "(" + to_sql_col_val(exps[0][0], cur_table) + " " + operator + " " + to_sql_col_val(exps[1][0], cur_table, expected_type) + ")"
    return (sql, return_type, "")

  else:
    # Both arguments are regular expressions.

    sql = "(" + to_sql_col_val(exps[0][0], cur_table) + " " + operator + " " + to_sql_col_val(exps[1][0], cur_table) + ")"
    return (sql, return_type, "")

