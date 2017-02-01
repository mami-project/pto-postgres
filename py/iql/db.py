import iql.convert as iqlc
import json
import pgdb

apilevel = '2.0'
threadsafety = 1
paramstyle = None #Is this even compliant? :(

def pg_connect(database = 'pto', user = 'user', password = 'password', config = iqlc.Config()):
  pg_con = pgdb.connect(database = database, user = user, password = password)
  con = Connection(pg_con, config)
  return con

class Error(BaseException):
  pass

class DatabaseError(Error):
  pass

class InterfaceError(Error):
  pass

class ProgrammingError(Error):
  pass

class NotSupportedError(Error):
  pass

class OperationalError(Error):
  pass

class Connection:

  def __init__(self, db_con, config):
    """
    Creates a connection.

    - db_con: DB-2 API connection (i.e. from pygresql)
    - config: iql.convert.Config
    """

    self.db_con = db_con
    self.config = config

  def commit(self):
    # Redirect to underlying connection
    
    try:
      return self.db_con.commit()
    except Exception as error:
      raise OperationalError(error)

  def rollback(self):
    # Redirect to underlying connection

    try:
      return self.db_con.rollback()
    except Exception as error:
      raise OperationalError(error)

  def cursor(self):
    # Redirect to underlying connection
    try:
      return Cursor(self.db_con.cursor(), self.db_con, self.config)
    except Exception as error:
      raise DatabaseError(error)

  def close(self):
    # Redirect to underlying connection
    
    try:
      return self.db_con.close()
    except Exception as error:
      raise DatabaseError(error)

class Cursor:
  
  def __init__(self, db_cursor, db_con, config):
    self.db_cursor = db_cursor
    self.db_con = db_con
    self.config = config
  
  def __getattr__(self, attr):
    # Redirect to underlying cursor

    return getattr(self.db_cursor, attr)

  def __setattr__(self, prop, val):
    # Redirect to underlying cursor
    if not prop in ['db_cursor','db_con']:
      return setattr(self.db_cursor, prop, val)

    else:
      super().__setattr__(prop, val)

  def callproc(self, procname, *parameters):
    """
    Not supported.
    """

    raise NotSupportedError()

  def close(self):
    # Redirect to underlying cursor
    return self.db_cursor.close()

  def execute(self, operation, *parameters):
    if(len(parameters) != 0):
      raise InterfaceError('Parameters are not accepted')

    # Convert to JSON if not already in JSON
    if(type(operation) == type('')):
      try:
        operation = json.loads(operation)
      except Exception as error:
        raise ProgrammingError(error)

    sql = None

  
    # Convert IQL
    try:
      sql = iqlc.convert(operation, self.config)
    except iqlc.IQLTranslationError as error:
      raise ProgrammingError(error)
    except Exception as error:
      raise ProgrammingError(error)

    # Pass SQL to underlying cursor
    try:
      self.db_cursor.execute(sql)
    except Exception as error:
      raise DatabaseError(error)

  def executemany(self, operation, seq_of_parameters):
    """
    Not supported.
    """

    raise NotSupportedError()

  def fetchone(self):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.fetchone()
    except Exception as error:
      raise DatabaseError(error)

  def fetchmany(self, size = 4096):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.fetchmany(size = size)
    except Exception as error:
      raise DatabaseError(error)

  def fetchall(self):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.fetchall()
    except Exception as error:
      raise DatabaseError(error)

  def nextset(self):
    """
    Not supported.
    """

    raise NotSupportedError()

  def setinputsizes(self, sizes):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.setinputsizes(sizes)
    except Exception as error:
      raise DatabaseError(error)

  def setoutputsize(self, size, *columns):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.setoutputsize(size, *columns)
    except Exception as error:
      raise DatabaseError(error)
