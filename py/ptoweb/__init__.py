from flask import Flask, g
from pg import DB
import iql.convert as iqlc

app = Flask(__name__)
app.config.from_envvar('PTO_PAPI_SETTINGS', silent=False)
app.config.from_envvar('PTO_PAPI_IQL_SETTINGS', silent = False)

from werkzeug.contrib.cache import FileSystemCache
cache = FileSystemCache('/tmp/ptoweb')

def get_db():
  dbname = app.config['DBNAME']
  user = app.config['USER']
  passwd = app.config['PASSWD']

  if not hasattr(g, 'psql_db'):
    g.psql_db = DB(dbname= dbname, user= user, passwd= passwd)

  return g.psql_db

def get_iql_config():
  IQL_TABLE = app.config['IQL_TABLE'];
  
  IQL_ATTR_TYPES = app.config['IQL_ATTR_TYPES'];

  IQL_MSMNT_TYPES = app.config['IQL_MSMNT_TYPES'];
  
  return iqlc.Config(msmnt_types = IQL_MSMNT_TYPES, expected_types = IQL_ATTR_TYPES, tbl_name = IQL_TABLE)


@app.teardown_appcontext
def close_db(error):
  if hasattr(g, 'psql_db'):
    g.psql_db.close()


import ptoweb.api


