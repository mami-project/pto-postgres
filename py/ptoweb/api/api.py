from ptoweb import cache, app, get_db, get_iql_config
from flask import Response, g, request
from bson import json_util
import json
from ptoweb.api.auth import require_auth
import re
from datetime import datetime
import iql.convert as iqlc
import pprint
import hashlib
from pg import escape_string
import os
import os.path
from werkzeug.utils import secure_filename

def sha1_hash(s):
  return hashlib.sha1(s.encode("utf-8")).hexdigest()



class CustomEncoder(json.JSONEncoder):
  def default(self, o):
    if(isinstance(o, datetime)):
      return o.timestamp()




def cors(resp):
  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

def json200(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=200, mimetype='application/json'))

def json400(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=400, mimetype='application/json'))

def json404(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=404, mimetype='application/json'))

def json500(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=404, mimetype='application/json'))

def text200(obj):
  return cors(Response(obj, status=200, mimetype='text/plain'))




def to_int(value):
  try:
    return int(value, 10)
  except:
    return 0



@app.route('/')
def api_index():
  """
  Dummy method answering with `{"status":"running"}` when the API is available.
  """

  for e in get_db().query("SELECT 1+1;").dictresult():
    print(e)

  return json200({'status':'running'})
  
 
 
@app.route("/result")
def api_result():
  query_id = request.args.get('id')


  sql = "SELECT * FROM query_queue WHERE id = '%s';" % (escape_string(query_id))

  try:
    dr = get_db().query(sql).dictresult()
  except:
    return json500({"error":"Internal Server Error"})


  if len(dr) <= 0:
    return json404({"error":"Not found!"})

  item = dr[0]
  if type(item['iql']) == type(''):
    item['iql'] = json.loads(item['iql'])

  if type(item['result']) == type(''):
    item['result'] = json.loads(item['result'])


  return json200(dr[0])



@app.route('/query')
def api_aquery():

  iql = request.args.get('q')

  if iql == None or iql == '':
    return json400({"error" : "Empty query!"})

  try:
    iql = json.loads(iql)
    iqls = json.dumps(iql, sort_keys = True)
  except:
    return json400({"error" : "Not valid JSON!"})

  iql_sql = ""

  try:
    iql_sql = iqlc.convert(iql, get_iql_config())
  except ValueError as error:
    return json400({"iql":iql, "error" : str(error)})

  query_hash = sha1_hash(iqls)


  sql = "SELECT * FROM query_queue WHERE id = '%s';" % (escape_string(query_hash))

  try:
    dr = get_db().query(sql).dictresult()
  except Exception as error:
    print(error)
    return json500({"error":"Internal Server Error"})

  if len(dr) > 0:
    first = dr[0]
    return json200({"query_id": first["id"], "already" : first})

  sql = "INSERT INTO query_queue(id, iql, sql_query, result, state) VALUES('%s', '%s'::JSONB, '%s', NULL, 'new');" % (escape_string(query_hash), escape_string(iqls), escape_string(iql_sql))

  try:
    get_db().query(sql)
  except Exception as error:
    print(error)
    return json500({"error":"Internal Server Error"})

  return json200({"query_id" : query_hash})



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


@app.route('/qq/running')
def api_qq_running():
  query = """
    SELECT start_time, id, iql,
    (CASE WHEN (stop_time IS NOT NULL) THEN 
         EXTRACT( EPOCH FROM (stop_time - start_time) )
     ELSE 
       EXTRACT(
           EPOCH FROM ( (NOW()::TIMESTAMP WITHOUT TIME ZONE) - start_time )
       )
     END) as duration 
      FROM query_queue WHERE state = 'running' ORDER BY start_time ;
  """

  try:
    dr = get_db().query(query).dictresult()
    return json200(dr)
  except Exception as error:
    print(error)
    return json500({"error":"Internal Server Error"})


@app.route('/qq/new')
def api_qq_new():
  query = """
    SELECT start_time, id, iql,
    (CASE WHEN (stop_time IS NOT NULL) THEN 
         EXTRACT( EPOCH FROM (stop_time - start_time) )
     ELSE 
       EXTRACT(
           EPOCH FROM ( (NOW()::TIMESTAMP WITHOUT TIME ZONE) - start_time )
       )
     END) as duration 
      FROM query_queue WHERE state = 'new' ORDER BY start_time ;
  """

  try:
    dr = get_db().query(query).dictresult()
    return json200(dr)
  except Exception as error:
    print(error)
    return json500({"error":"Internal Server Error"})


@app.route('/qq/get')
def api_qq_get():
  query = """
    SELECT * FROM query_queue WHERE id = '%s';
  """ % (escape_string(request.args.get('id')))

  try:
    dr = get_db().query(query).dictresult()
    return json200(dr)
  except Exception as error:
    print(error)
    return json500({"error":"Internal Server Error"})


@app.route('/raw/upload', methods=['POST'])
def api_raw_upload():
  if 'data' not in request.files:
    return json400({"error":"File is missing"})

  metadata = request.args.get('metadata')
  print(metadata)

  if metadata == None:
    return json400({"error" : "Metadata missing!"})

  try:
    metadata = json.loads(metadata)
  except:
    return json400({"error":"Not valid JSON!"})

  if (not ('filename' in metadata)) or (not ('campaign' in metadata)):
    return json400({"error" : "Missing filename and/or campaign!"})

  if not isinstance(metadata['filename'], str) or not isinstance(metadata['campaign'], str):
    return json400({"error" : "Wrong type for filename and/or campaign"})

  data = request.files['data']
  secure_campaign_ = secure_filename(metadata['campaign'])
  secure_filename_ = secure_filename(metadata['filename'])
  path = os.path.join(secure_campaign_, secure_filename_)

  path_prefix = '/tmp'
  
  if not os.path.isdir(os.path.join(path_prefix, secure_campaign_)):
    os.mkdir(os.path.join(path_prefix, secure_campaign_))
  
  save_path = os.path.join(path_prefix, path)

  if os.path.exists(save_path):
    return json400({"error" : "File already exists!"})

  data.save(os.path.join(path_prefix, path))

  return json200({"msg":"OK"})
