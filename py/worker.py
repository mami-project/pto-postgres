import sys
import json
from pg import DB, escape_string
from datetime import datetime
import time
import threading as th
import random

class CustomEncoder(json.JSONEncoder):
  def default(self, o):
    if(isinstance(o, datetime)):
      return o.timestamp()


def remove_nulls(d):
  for key in list(d.keys()):
    if d[key] == None:
      if(key.startswith('val_')):
        del d[key]
    elif key.startswith('val_'):
      d[key.replace(key,'value')] = d[key]
      del d[key]

  return d

class Worker(th.Thread):

  def __init__(self, dbname, user, passwd, thid, tbl_name = 'query_queue'):
    th.Thread.__init__(self) 
    self.db = DB(dbname = dbname, user = user, passwd = passwd)
    self.thid = thid
    self.TBL_NAME = tbl_name

  def list_new(self):
    dr = self.db.query("SELECT * FROM %s WHERE state = 'new'" % self.TBL_NAME)
    dr = dr.dictresult()

    return dr

  def find_and_process_new(self, f):

    time_now = int(datetime.utcnow().timestamp())

    dr = self.db.query("""
         UPDATE %s SET state = 'running',
                       start_time = to_timestamp('%d')::TIMESTAMP WITHOUT TIME ZONE
         WHERE state = 'new' AND id = (SELECT id FROM %s WHERE state = 'new' ORDER BY id ASC LIMIT 1)
         RETURNING id, state, iql, sql_query;""" % (self.TBL_NAME, time_now, self.TBL_NAME))
    dr = dr.dictresult()

    if len(dr) == 0 or len(dr) > 1:
      print('Worker%d found no new queries' % self.thid)
      return False # Nothing to do
    

    item = dr[0]

    print('Worker#%d processing query %s' % (self.thid, item['id']))

    result = {}

    try:
      result = f(item['sql_query'])
    except Exception as error:
      print(error)
      time_now = int(datetime.utcnow().timestamp())
      self.db.query("""
      UPDATE %s SET state = 'failed', result = '%s',
                    stop_time = to_timestamp('%d')::TIMESTAMP WITHOUT TIME ZONE
      WHERE id = '%s';""" % (self.TBL_NAME, escape_string(json.dumps(result, sort_keys = True, cls = CustomEncoder)), time_now, escape_string(item['id'])))
      
      print('Worker#%d completed %s with FAILED' % (self.thid, item['id']))

      return None

    time_now = int(datetime.now().timestamp())

    self.db.query("""
    UPDATE %s SET state = 'done', result = '%s'::JSONB,
                  stop_time = to_timestamp('%d')::TIMESTAMP WITHOUT TIME ZONE
    WHERE id = '%s';""" % (self.TBL_NAME, escape_string(json.dumps(result, sort_keys = True, cls = CustomEncoder)), time_now, escape_string(item['id'])))

    print('Worker#%d completed %s with SUCCESS' % (self.thid, item['id']))

    return True

  def sql_query(self, query):
    dr = self.db.query(query).dictresult()
    result_json = []

    i = 0

    for e in dr:
      remove_nulls(e)
      result_json.append(e)
      i += 1
      if(i > 8192): break

    return {"results":result_json}

  def run(self):
    while True:
      self.find_and_process_new(self.sql_query)
      time.sleep(random.randint(1,120))

print(sys.argv)

db=input('DB? ')
user=input('User? ')
pwd=input('Pwd? ')
num_workers=int(input('Number of workers? '))

print('Launching workers...')

workers = []
i = 0
while i < num_workers:
  worker = Worker(db, user, pwd, i)
  workers.append(worker)
  worker.start()
  print('Launched worker#%d' % i)
  i += 1

for worker in workers:
  worker.join()
