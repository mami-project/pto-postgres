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
import hashlib

def sha1_hash(s):
  return hashlib.sha1(s.encode("utf-8")).hexdigest()


def sha1_file_hash(fobj, chunk_size = 8192):
  """
  Calculate sha1 hash of a file object chunk-wise.

  Args:
    fobj - File object (read(size))
    chunk_size - Size of chunks to read (default 8192)

  Returns: sha1 hash as string, hex/lowercase
  """

  md = hashlib.sha1()
  while True:
    chunk = fobj.read(chunk_size)
    if len(chunk) == 0:
      break
    md.update(chunk)

  return md.hexdigest()


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


def insert_upload(filesystem_path, campaign, file_hash, start_time, stop_time, uploader, metadata):
  """
  Insert an upload
  """

  filesystem_path = escape_string(filesystem_path)
  campaign = escape_string(campaign)
  file_hash = escape_string(file_hash)
  uploader = escape_string(uploader)
  metadata = escape_string(json.dumps(metadata))

  sql = """
  INSERT INTO uploads(
    filesystem_path,
    campaign,
    file_hash,
    start_time,
    stop_time,
    uploader,
    metadata,
    time_of_upload)

  VALUES(
    '%s',
    '%s',
    '%s',
    to_timestamp(%d) :: TIMESTAMP WITHOUT TIME ZONE,
    to_timestamp(%d) :: TIMESTAMP WITHOUT TIME ZONE,
    '%s',
    '%s' :: JSONb,
    to_timestamp(%d) :: TIMESTAMP WITHOUT TIME ZONE);
  """ % (filesystem_path, campaign, file_hash, start_time, stop_time, uploader, metadata, datetime.utcnow().timestamp())

  get_db().query(sql)

  return True

def check_permissions(key, required_permissions):
  """
  Check permissions based on api key
  """

  if not isinstance(key, str):
    return False

  try:
    for e in get_db().query("SELECT * FROM api_keys WHERE key = '%s';" % (escape_string(key))).dictresult():
      if not 'permissions' in e:
        return False

      permissions = e['permissions']

      if not isinstance(permissions, str):
        return False

      for required_permission in required_permissions:
        if not required_permission in permissions:
          return False

      return e['name']
  except Exception as error:
    print(error)
    return False

  return False

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
  key = request.headers.get('X-API-KEY')

  uploader = check_permissions(key, 'u')

  if not uploader:
    return json400({"error": "Insufficient permissions or invalid API key"}) 

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

  if (not ('start_time' in metadata)) or (not ('stop_time' in metadata)):
    return json400({"error" : "Missing start_time and/or stop_time!"})

  if not isinstance(metadata['start_time'], int) or not isinstance(metadata['stop_time'], int):
    return json400({"error" : "Wrong type for start_time and/or stop_time!"})

  data = request.files['data']

  file_hash = sha1_file_hash(data.stream)
  start_time = metadata['start_time']
  stop_time = metadata['stop_time']
  campaign = metadata['campaign']

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

  try:
    insert_upload(save_path, campaign, file_hash, start_time, stop_time, uploader, metadata)
  except Exception as error:
    print(error)
    return json500({"error" : "Internal error!"})

  return json200({"file_hash":file_hash})
