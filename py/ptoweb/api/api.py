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


@app.route('/')
def api_index():
  """
  Dummy method answering with `{"status":"running"}` when the API is available.
  """

  for e in get_db().query("SELECT 1+1;").dictresult():
    print(e)

  return json200({'status':'running'})


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
  for key in d.keys():
    if d[key] == None:
      del d[key]
    elif key.startswith('val_i'):
      d[key.replace('val_i','value')] = d[key]
      del d[key]
    elif key.startswith('val_s'):
      d[key.replace('val_s','value')] = d[key]
      del d[key]

  return d


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


