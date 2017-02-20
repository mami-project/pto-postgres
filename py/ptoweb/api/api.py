from ptoweb import cache, app, get_db, get_iql_config
from flask import Response, g, request, send_file
from bson import json_util
import json
from ptoweb.api.auth import require_auth
from ptoweb.api.util import put_to_cache, get_from_cache
import re
from datetime import datetime
import iql.convert as iqlc
import pprint
import hashlib
from pg import escape_string
import pg
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
    if(isinstance(o, pg.Decimal)):
      return float(str(o))
    return str(o);




def cors(resp):
  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

def json200(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=200, mimetype='application/json'))

def json400(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=400, mimetype='application/json'))

def json429(obj):
  return cors(Response(json.dumps(obj, cls=CustomEncoder), status=429, mimetype='application/json'))

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


def get_upload_stats():
  """
  Return upload statistics
  """

  stats = get_from_cache('upload-stats')
  print(stats)

  if stats != None:
    return stats

  sql = """
  SELECT campaign, count(*) as count_, 
         MIN(start_time) AS first_msmnt,
         MAX(stop_time) AS last_msmnt,
         SUM((metadata ->> 'file_size')::BIGINT)/(1024.0*1024.0) as file_size
  FROM uploads GROUP BY campaign;
  """

  dr = get_db().query(sql).dictresult()

  stats = {}
  for e in dr:
    stats[e['campaign']] = {'count' : e['count_'], 
       'first_msmnt' : e['first_msmnt'],
       'last_msmnt' : e['last_msmnt'],
       'file_size' : e['file_size']}

  put_to_cache('upload-stats', stats, timeout = 15 * 60)

  return stats


def count_queued_queries():
  """
  Return number of queries WAITING in the queue
  """

  sql = """
  SELECT COUNT(*) AS count_ FROM query_queue WHERE state = 'new';
  """

  dr = get_db().query(sql).dictresult()

  if len(dr) != 1:
    raise Exception("Couldn't count queued queries")

  return dr[0]['count_']


def revoke_api_key(api_key):
  """
  Drop all permissions.
  """

  api_key = escape_string(api_key)

  sql = """
  UPDATE api_keys SET permissions = ''
  WHERE key = '%s';
  """ % (api_key)

  get_db().query(sql)

  return True  


def find_uploads_by_filesystem_path(filesystem_path):
  """
  Find uploads with a given path.
  """

  filesystem_path = escape_string(filesystem_path)

  sql = """
  SELECT * FROM uploads WHERE filesystem_path = '%s';
  """ % (filesystem_path)

  return get_db().query(sql).dictresult()


def find_uploads_by_campaign(campaign):
  """
  Find uploads with a given campaign
  """

  campaign = escape_string(campaign)

  sql = """
  SELECT * FROM uploads WHERE campaign = '%s';
  """ % (campaign)

  return get_db().query(sql).dictresult()


def find_uploads_by_file_hash(file_hash):
  """
  Find uploads with a given file_hash
  """

  file_hash = escape_string(file_hash)

  sql = """
  SELECT * FROM uploads WHERE file_hash = '%s';
  """ % (file_hash)

  return get_db().query(sql).dictresult()


def get_recent_queries():
  """
  Return 12 most recent queries.
  """

  sql = """
  SELECT id, iql FROM query_queue WHERE state = 'done'
  ORDER BY start_time DESC LIMIT 12;
  """

  return get_db().query(sql).dictresult()


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

def check_permissions_request(req, required_permissions):
  key = req.headers.get("X-API-KEY")
  return check_permissions(key, required_permissions)


def expand_permissions(permissions):

  # u includes r
  if 'u' in permissions:
    if not 'r' in permissions:
      permissions += 'r'

  return permissions


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

      permissions = expand_permissions(e['permissions'])

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

  
@app.route("/revoke-key")
def api_revoke_key():
  """
  Revoke API key. Call this when you suspect your API key is not
  secret anymore.
  """

  if not check_permissions_request(request, ''):
    return json400({"error" : "Insufficient permissions or invalid API key!"})

  api_key = request.headers.get('X-API_KEY')
  
  if api_key != None:
    try:
      revoke_api_key(api_key)

    except Exception as error:
      print(error)
      return json500({"error" : "Internal Server Error"})

  return json200({"msg":"ok"}) 
 

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


def check_rate_limit(req, max_reqs = 4):
  if req.remote_addr == None or req.remote_addr == '':
    return False

  counter = get_from_cache('rate-limit/' + req.remote_addr)

  if counter == None:
    counter = 1
  else:
    counter += 1

  put_to_cache('rate-limit/' + req.remote_addr, counter, timeout = 24*60*60)

  if counter > max_reqs:
    return False

  return True


@app.route('/rate-limit')
def api_rate_limit():

  if not check_rate_limit(request):
    return json429({"error" : "Too many requests!"})

  return json200({"msg":"ok"})


@app.route('/upload-stats')
def api_upload_stats():
  try:
    return json200(get_upload_stats())

  except Exception as error:
    print(error)
    return json500({"error": "Internal Server Error"})


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

  if not check_rate_limit(request):
    return json429({"error" : "Too many requests!"})

  try:
    queued_queries_count = count_queued_queries()
  except Exception as error:
    print(error)
    return json500({"error" : "Internal Server Error"})

  if(queued_queries_count >= 10):
    return json400({"error" : "Currently we are experiencing high load. Please try again another day!"})

  time_now = int(datetime.utcnow().timestamp())

  sql = "INSERT INTO query_queue(id, iql, sql_query, result, state, submit_time) VALUES('%s', '%s'::JSONB, '%s', NULL, 'new','%d');" % (escape_string(query_hash), escape_string(iqls), escape_string(iql_sql), time_now)

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


@app.route('/qq/recent')
def api_qq_recent():
  try:
    return json200(get_recent_queries())

  except Exception as error:
    print(error)
    return json500({"error": "Internal Server Error"})


@app.route('/qq/summary')
def api_qq_summary():
  sql = """
  SELECT id, state, iql, duration FROM (
  (SELECT stop_time, id, state, iql,
   (CASE WHEN ( (stop_time IS NOT NULL) AND (start_time IS NOT NULL) ) THEN
     EXTRACT ( EPOCH FROM (stop_time - start_time ) )
    ELSE
     (CASE WHEN (start_time IS NOT NULL) THEN
       EXTRACT ( EPOCH FROM ((NOW() AT TIME ZONE 'UTC') - start_time))
      ELSE
       EXTRCACT ( EPOCH FROM ((NOW() AT TIME ZONE 'UTC') - submit_time)) END) END) AS duration
  FROM query_queue WHERE state = 'running' OR state = 'new' OR state = 'failed')
  UNION
  (SELECT stop_time, id, state, iql,
   (CASE WHEN ( (stop_time IS NOT NULL) AND (start_time IS NOT NULL) ) THEN
     EXTRACT ( EPOCH FROM (stop_time - start_time ) )
    ELSE
     (CASE WHEN (start_time IS NOT NULL) THEN
       EXTRACT ( EPOCH FROM ((NOW() AT TIME ZONE 'UTC') - start_time))
      ELSE
       NULL END) END) AS duration
  FROM query_queue WHERE state = 'done' ORDER BY stop_time DESC
  LIMIT 12)) summary ORDER BY stop_time DESC;
  """
  
  try:
    dr = get_db().query(sql).dictresult()
    return json200(dr)
  except Exception as error:
    print(error)
    return json500({"error" : "Internal Server Error!"})


@app.route('/qq/running')
def api_qq_running():
  query = """
    SELECT start_time, id, iql,
    (CASE WHEN (stop_time IS NOT NULL) THEN 
         EXTRACT( EPOCH FROM (stop_time - start_time) )
     ELSE 
       EXTRACT(
           EPOCH FROM ( ((NOW() AT TIME ZONE 'UTC')::TIMESTAMP WITHOUT TIME ZONE) - start_time )
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
           EPOCH FROM ( ((NOW() AT TIME ZONE 'UTC')::TIMESTAMP WITHOUT TIME ZONE) - start_time )
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


@app.route('/raw/download')
def api_raw_download():
  """
  Download file
  """

  doer = check_permissions_request(request, 'r')
  if not doer:
    return json400({"error" : "Insufficietn permissions or invalid API key!"})

  filesystem_path = request.args.get('filesystem_path')

  if (filesystem_path == None or filesystem_path == ''):
    return json400({"error" : "Missing filesystem_path"})

  download_path = None

  try:
    uploads = find_uploads_by_filesystem_path(filesystem_path)

    if len(uploads) == 0:
      return json404({"error": "Not found!"})

    download_path = uploads[0]['filesystem_path']

  except Exception as error:
    return json500({"error" : "Internal Server Error"})

  download_path = os.path.join(app.config['RAW_UPLOAD_FOLDER'], download_path)
  print(download_path)
  return send_file(download_path, mimetype = "application/octet-stream")


@app.route('/raw/upload-entries')
def api_raw_upload_entries():
  """
  Get all upload entries for a campaign.
  """

  doer = check_permissions_request(request, 'r')
  if not doer:
    return json400({"error": "Insufficiont permissions or invalid API key!"})

  campaign = request.args.get('campaign')
  if campaign == None or campaign == '':
    return json400({"error": "Missing campaign!"})

  try:
    upload_entries = find_uploads_by_campaign(campaign)
    return json200(upload_entries)
  except Exception as error:
    print(error)
    return json400({"error" : "Internal error!"})




@app.route('/raw/upload-entry')
def api_raw_upload_entry():
  """
  Get a raw upload entry
  """

  doer = check_permissions_request(request, 'u')
  if not doer:
    return json400({"error" : "Insufficient permissions or invalid API key!"})

  filesystem_path = request.args.get('filesystem_path')
  file_hash = request.args.get('file_hash')

  if (filesystem_path == None or filesystem_path == '') and (file_hash == None or file_hash == ''):
    return json400({"error" : "Missing filesystem_path or file_hash!"})

  try:
    if filesystem_path != None and filesystem_path != '':
      return json200(find_uploads_by_filesystem_path(filesystem_path))
    else:
      return json200(find_uploads_by_file_hash(file_hash))
  except Exception as error:
    print(error)
    return json500({"error" : "Internal Server Error!"})


@app.route('/raw/upload', methods=['POST'])
def api_raw_upload():
  """
  Upload a raw file to the observatory.
  """

  key = request.headers.get('X-API-KEY')

  uploader = check_permissions(key, 'u')

  if not uploader:
    return json400({"error": "Insufficient permissions or invalid API key!"})

  if 'data' not in request.files:
    return json400({"error":"File is missing!"})

  metadata = request.args.get('metadata')
  print(metadata)

  if metadata == None:
    return json400({"error" : "Metadata missing!"})

  try:
    metadata = json.loads(metadata)
  except:
    return json400({"error":"Not valid JSON!"})

  if (not ('filetype' in metadata)):
    return json400({"error" : "Filetype is missing!"})

  if not isinstance(metadata['filetype'], str):
    return json400({"error" : "Wrong type!"})

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
  data.stream.seek(0) #jump back to beginning
  start_time = metadata['start_time']
  stop_time = metadata['stop_time']
  campaign = metadata['campaign']

  secure_campaign_ = secure_filename(metadata['campaign'])
  secure_filename_ = secure_filename(metadata['filename'])
  secure_filetype_ = secure_filetype(metadata['filetype'])
  path = os.path.join(secure_campaign_, secure_filetype_, secure_filename_)

  path_prefix = app.config['RAW_UPLOAD_FOLDER']
  
  if not os.path.isdir(os.path.join(path_prefix, secure_campaign_)):
    os.mkdir(os.path.join(path_prefix, secure_campaign_))

  if not os.path.isdir(os.path.join(path_prefix, secure_campaign_, secure_filetype_)):
    os.mkdir(os.path.join(path_prefix, secure_campaign_, secure_filetype_))
  
  save_path = os.path.join(path_prefix, path)

  if os.path.exists(save_path):
    return json400({"error" : "File already exists!"})

  data.save(os.path.join(path_prefix, path))

  try:
    file_size = os.path.getsize(os.path.join(path_prefix, path))
    metadata['file_size'] = file_size
    insert_upload(path, campaign, file_hash, start_time, stop_time, uploader, metadata)
  except Exception as error:
    print(error)
    return json500({"error" : "Internal Server Error!"})

  return json200({"file_hash":file_hash,"filesystem_path":path})
