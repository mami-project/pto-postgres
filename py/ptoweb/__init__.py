from flask import Flask, g
from pg import DB

app = Flask(__name__)
app.config.from_envvar('PTOWEB_SETTINGS', silent=False)

from werkzeug.contrib.cache import FileSystemCache
cache = FileSystemCache('/tmp/ptoweb')

def get_db():
  dbname = app.config['DBNAME']
  user = app.config['USER']
  passwd = app.config['PASSWD']

  if not hasattr(g, 'psql_db'):
    g.psql_db = DB(dbname= dbname, user= user, passwd= passwd)

  return g.psql_db


@app.teardown_appcontext
def close_db(error):
  if hasattr(g, 'psql_db'):
    g.psql_db.close()


import ptoweb.api


