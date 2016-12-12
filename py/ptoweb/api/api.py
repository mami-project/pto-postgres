from ptoweb import cache, app, get_db
from flask import Response, g, request
from bson import json_util
import json
from ptoweb.api.auth import require_auth
from ptoweb.api.iql_constants import *
import re
from datetime import datetime
import iql.convert as iqlc
import pprint

class CustomEncoder(json.JSONEncoder):
  def default(self, o):
    if(isinstance(o, datetime)):
      return o.timestamp()

def get_iql_config():
  return iqlc.Config(msmnt_types = DICT_MSMNT_TYPES, expected_types = DICT_EXPECTED_TYPES_ATTR, all_sql_attrs = ALL_SQL_ATTRS)

def cors(resp):
  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

def json200(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=200, mimetype='application/json'))

def json400(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=400, mimetype='application/json'))

def json404(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=404, mimetype='application/json'))

def text200(obj):
  return cors(Response(obj, status=200, mimetype='text/plain'))

def to_int(value):
  try:
    return int(value, 10)
  except:
    return 0


@app.route('/attributes')
def api_iql_info():

  data_structure = [{"name":"ecn.connectivity","measurement" : True, "type" : "S", "values" : ["works","broken","offline","transient"]},
                    {"name":"ecn.negotiated", "measurement" : True, "type" : "N", "values" : [0,1]},
                    {"name":"ecn.site_dependent", "measurement" : True, "type" : "*S"},
                    {"name":"ecn.path_dependent", "measurement" : True, "type" : "*S"}]

  for e_types in DICT_EXPECTED_TYPES_ATTR:
    data_structure.append ( {"name" : e_types, "measurement" : False, "type" : DICT_EXPECTED_TYPES_ATTR[e_types]} )

  return json200(data_structure)


@app.route('/')
def api_index():
  """
  Dummy method answering with `{"status":"running"}` when the API is available.
  """

  for e in get_db().query("SELECT 1+1;").dictresult():
    print(e)

  return json200({'status':'running'})


def convert_row(row):
  if 'name' in row:
    if row['name'] == 'ecn.connectivity':
      row['conditions'] = ["ecn.connectivity." + row['value']]
    elif row['name'] == 'ecn.negotiated':
      if row['value'] == 0:
        row['conditions'] = ['ecn.not_negiotiated']
      elif row['value'] == 1:
        row['conditions'] = ['ecn.negotiated']
    del row['name']
    del row['value']

  if 'time_to' in row and 'time_from' in row:
    time_to = row['time_to']
    time_from = row['time_from']

    row['time'] = {'to' : {'$date' : time_to.timestamp()*1000}, 'from' : {'$date' : time_from.timestamp()*1000}}
    del row['time_to']
    del row['time_from']

  if 'oid' in row:
    row['id'] = {'$oid' : str(row['oid'])}

  del row['oid']
  del row['path_id']


  del row['full_path']
  row['path'] = row['path_nodes']
  del row['path_nodes']

  row['sources'] = {}
  row['value'] = {}
    


@app.route('/old')
def api_old():
  sip = request.args.get('sip')
  dip = request.args.get('dip')

  on_path = request.args.get('on_path')

  if on_path:
    on_path = on_path.split(',')

  time_from = int(to_int(request.args.get('from')) / 1000.0)
  time_to = int(to_int(request.args.get('to')) / 1000.0)

  conditions = request.args.get('conditions')

  dnf = []

  if conditions:
    and_terms = conditions.split(',')
    for and_term in and_terms:
      and_term = and_term.split(':')
      dnf.append(and_term)

  iql_ands = []
  for and_term in dnf:
    ands = []
    for condition in and_term:
      if condition.startswith('ecn.connectivity'):
        value = condition[17:]
        ands.append({"eq":["$ecn.connectivity", value]})
    iql_ands.append({"and":ands})

  iql_dnf = {"or": iql_ands}

  iql_query_parts = [iql_dnf]

  if sip:
    iql_query_parts.append({"eq":["@sip", sip]})

  if dip:
    iql_query_parts.append({"eq":["@dip", dip]})

  iql_query_parts.append({"ge":["@time_from", {"time":[time_from]}]})
  iql_query_parts.append({"le":["@time_to", {"time":[time_to]}]})

  

  iql_query = ({"query":{"all":[{"simple":[{"and":iql_query_parts}]}]}})
  
  try:
    sql = iqlc.convert(iql_query, get_iql_config())
  except ValueError as error:
    return json400({"error" : str(error)})

  dr = get_db().query(sql).dictresult()
  result_json = []

  i = 0

  for e in dr:
    
    remove_nulls(e)
    convert_row(e)

    result_json.append(e)

    i += 1
    if(i > 128): break

  return json200({"count": len(result_json), "results" : result_json})
  
  
  


@app.route('/query')
def api_query():

  iql = request.args.get('q')

  if iql == None or iql == '':
    return json400({"error" : "Empty query!"})

  try:
    iql = json.loads(iql)
  except:
    return json400({"error" : "Not valid JSON!"})

  try:
    sql = iqlc.convert(iql, get_iql_config())
  except ValueError as error:
    return json400({"error" : str(error)})

  dr = get_db().query(sql).dictresult()
  result_json = []

  i = 0

  for e in dr:
    
    remove_nulls(e)

    result_json.append(e)

    i += 1
    if(i > 128): break

  return json200({"results" : result_json})


def remove_nulls(d):
  for key in list(d.keys()):
    if d[key] == None:
      del d[key]
    elif key.startswith('val_'):
      d[key.replace(key,'value')] = d[key]
      del d[key]

  return d


@app.route('/sql')
def api_sql():
  iql = request.args.get('q')

  if iql == None or iql == '':
    return json400({"error" : "Empty query!"})

  try:
    iql = json.loads(iql)
  except:
    return json400({"error" : "Not valid JSON!"})

  #try:
  sql = iqlc.convert(iql, get_iql_config())
  #except ValueError as error:
  #  return json400({"error" : str(error)})

  return text200(sql)



@app.route('/translate')
def api_translate():

  iql = request.args.get('q')

  if iql == None or iql == '':
    return json400({"error" : "Empty query!"})

  try:
    iql = json.loads(iql)
  except:
    return json400({"error" : "Not valid JSON!"})

  try:
    sql = iqlc.convert(iql, get_iql_config())
  except ValueError as error:
    return json400({"error" : str(error)})

  pp = pprint.PrettyPrinter(indent = 2)
  piql = pp.pformat(iql)

  lines = piql.splitlines()
  piql = '\n'.join(map(lambda a: '-- ' + a, lines))

  dr = get_db().query(sql).dictresult()
  result_json = ""

  i = 0

  for e in dr:
    
    remove_nulls(e)

    result_json += json.dumps(e, cls=CustomEncoder) + "\n"

    i += 1
    if(i > 128): break

 
  return text200(piql + "\n\n" + sql + "\n\n" + result_json)


def to_int(value):
  try:
    return int(value, 10)
  except:
    return 0


