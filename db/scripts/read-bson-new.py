import bson
import datetime
import sys
from pg import escape_string, DB
import json

path = sys.argv[1]

dbname = sys.argv[2]
user = sys.argv[3]
pwd = sys.argv[4]

db = DB(dbname = dbname, user = user, passwd = pwd)

f = open(path,'rb')
it = bson.decode_file_iter(f)

i = 0

condition_resolution_map = {
  "ecn.connectivity.works" : 2,
  "ecn.connectivity.broken" : 3,
  "ecn.connectivity.transient" : 4,
  "ecn.connectivity.offline" : 5,
  "ecn.negotiated" : 7,
  "ecn.not_negotiated" : 8,
  "ecn.connectivity.super.works" : 13,
  "ecn.connectivity.super.broken" : 14,
  "ecn.connectivity.super.transient" : 15,
  "ecn.connectivity.super.offline" : 16,
  "ecn.connectivity.super.weird" : 17,
  "ecn.path_dependent.weak" : 19,
  "ecn.path_dependent.strong" : 20,
  "ecn.path_dependent.strict" : 21,
  "ecn.site_dependent.weak" : 23,
  "ecn.site_dependent.strong" : 24,
  "ecn.site_dependent.strict" : 25,
  "ecn.ect_zero.seen" : 26,
  "ecn.ect_one.seen" : 27,
  "ecn.ce.seen" : 28
}

def resolve_condition(condition):
  global condition_resolution_map
  if not (condition in condition_resolution_map):
    raise ValueError("Unknown condition %s" % condition)

  if condition == 'ecn.negotiated':
    return 'ecn.negotiation_attempt.succeeded'
  elif condition == 'ecn.not_negotiated':
    return 'ecn.negotiation_attempt.failed'

  return condition

in_transaction = False
bulks = 0

for doc in it:

  if not in_transaction:
    db.query("BEGIN;")
    in_transaction = True

  # Make sure this is a valid observation
  #  If action_ids is empty something is terribly wrong
  #  If the first action_id's valid flag isn't true skip.
  action_ids = doc['action_ids']
  if(len(action_ids) <= 0):
    continue
  if(not action_ids[0]['valid']):
    continue

  toc = action_ids[0]['id'];  
  full_path = doc['path']
  conditions = doc['conditions']
  conditions = list(map(resolve_condition, conditions))
  time_from = doc['time']['from']
  time_to = doc['time']['to']
  analyzer = doc['analyzer_id']
  metadata = doc['value']

  full_path = ','.join(list(map(lambda a: "'" + escape_string(a) + "'", full_path)))
  conditions = list(map(escape_string, conditions))
  time_from = escape_string(time_from.isoformat())
  time_to = escape_string(time_to.isoformat())
  metadata = escape_string(json.dumps(metadata, sort_keys = True))
  analyzer = escape_string(analyzer)
  toc = int(toc)

  for condition in conditions:

    sql =  """
       INSERT INTO observation_fixed(full_path, name, time_from, time_to, metadata, analyzer, val_n, time_of_creation, time_of_invalidation, observation_set)
        VALUES(ARRAY[%s]::VARCHAR[], '%s', '%s'::TIMESTAMP WITHOUT TIME ZONE, '%s'::TIMESTAMP WITHOUT TIME ZONE,
               '%s'::JSON, '%s', %d, %d, %d, %d);
       """ % (full_path, condition, time_from, time_to, metadata, analyzer, 1, toc, 9999, toc)
    db.query(sql)

  i += 1
  if(i >= 10*1024):
    if in_transaction:
      print("Inserted %d bulk of %d" % (bulks,i))
      db.query("COMMIT;")
      in_transaction = False
      i = 0

      bulks += 1

      #if(bulks >= 10): break

if in_transaction:
  db.query("COMMIT;")
