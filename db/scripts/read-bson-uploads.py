import bson
import datetime
import sys
import pg
import json


f = open(sys.argv[1],'rb')
it = bson.decode_file_iter(f)

path_part = "hdfs://localhost:9000/uploads/"
campaigns = ['copycat-april',
             'ecn-august',
             'ecn-july',
             'ecn-june',
             'ecn-june16',
             'modern-times',
             'mustgofaster-tfo',
             'tracebox-16',
             'more-is-better']

for doc in it:
  file_hash = doc['sha1']
  hdfs_path = doc['path']
  campaign = doc['meta']['msmntCampaign']

  if not hdfs_path.startswith(path_part):
    #print("Ignoring " + hdfs_path)
    continue

  if not campaign in campaigns:
    #print("Ignoring " + campaign)
    continue

  time_of_upload = doc['timestamp']
  path = hdfs_path.replace(path_part, "")

  if 'seqKey' in doc:
    path += '#' + doc['seqKey']

  uploader = doc['uploader']
  start_time = doc['meta']['start_time']
  stop_time = doc['meta']['stop_time']
  
  del doc['meta']['start_time']
  del doc['meta']['stop_time']
  del doc['meta']['msmntCampaign']

  metadata = json.dumps(doc['meta'])  

  sql = """
  INSERT INTO uploads(filesystem_path, campaign, file_hash, time_of_upload, start_time, stop_time, metadata, uploader)
   VALUES('%s', '%s', '%s', to_timestamp(%d)::TIMESTAMP WITHOUT TIME ZONE,
   to_timestamp(%d)::TIMESTAMP WITHOUT TIME ZONE,
   to_timestamp(%d)::TIMESTAMP WITHOUT TIME ZONE,
   '%s'::JSONb, '%s');
  """ % (pg.escape_string(path), pg.escape_string(campaign), pg.escape_string(file_hash), time_of_upload, start_time.timestamp(), stop_time.timestamp(), metadata, uploader)
  print(' '.join(sql.splitlines()))
