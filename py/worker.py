import sys
import json
import iql.convert as iqlc
from iql_constants import *

from pg import DB, escape_string


def get_iql_config():
  return iqlc.Config(msmnt_types = DICT_MSMNT_TYPES, expected_types = DICT_EXPECTED_TYPES_ATTR, all_sql_attrs = ALL_SQL_ATTRS)


def remove_nulls(d):
  for key in list(d.keys()):
    if d[key] == None:
      del d[key]
    elif key.startswith('val_'):
      d[key.replace(key,'value')] = d[key]
      del d[key]

  return d

class Worker:

  def __init__(self, dbname, user, passwd):
    self.db = DB(dbname = dbname, user = user, passwd = passwd)

    self.TBL_NAME = 'query_queue'

  def list_new(self):
    dr = self.db.query("SELECT * FROM %s WHERE state = 'new'" % self.TBL_NAME)
    dr = dr.dictresult()

    return dr

  def find_and_process_new(self, f):
    dr = self.db.query("""
         UPDATE %s SET state = 'running'
         WHERE state = 'new' AND id = (SELECT id FROM %s WHERE state = 'new' ORDER BY id ASC LIMIT 1)
         RETURNING id, state, iql;""" % (self.TBL_NAME, self.TBL_NAME))
    dr = dr.dictresult()

    if len(dr) == 0 or len(dr) > 1:
      return False # Nothing to do
    

    item = dr[0]

    result = {}

    try:
      result = f(item['iql'])
    except Exception as error:
      print(error)
      self.db.query("""
      UPDATE %s SET state = 'failed', result = '%s'::JSON
      WHERE id = '%s';""" % (self.TBL_NAME, escape_string(json.dumps(result, sort_keys = True)), escape_string(item['id'])))
      return None

    self.db.query("""
    UPDATE %s SET state = 'done', result = '%s'::JSON
    WHERE id = '%s';""" % (self.TBL_NAME, escape_string(json.dumps(result, sort_keys = True)), escape_string(item['id'])))

    return True

  def iql_query(self, query):
    print(type(query))
    print(query)

    try:
      sql = iqlc.convert(query, get_iql_config())
    except ValueError as error:
      return {"error" : str(error)}

    dr = self.db.query(sql).dictresult()
    result_json = []

    i = 0

    for e in dr:
      remove_nulls(e)
      result_json.append(e)
      i += 1
      if(i > 128): break

    return {"results":result_json}

print(sys.argv)

worker = Worker(sys.argv[1], sys.argv[2], sys.argv[3])
print(worker.find_and_process_new(worker.iql_query))
