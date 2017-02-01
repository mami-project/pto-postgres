import iql.convert as iqlc
import json

apilevel = '2.0'
threadsafety = 1
paramstyle = None #Is this even compliant? :(

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

    self.db_con = db_con()
    self.config = config

  def commit(self):
    # Redirect to underlying connection
    
    try:
      return self.db_con.commit()
    except error:
      raise OperationalError(error)

  def rollback(self):
    # Redirect to underlying connection

    try:
      return self.db_con.rollback()
    except error:
      raise OperationalError(error)

  def cursor(self):
    # Redirect to underlying connection
    try:
      return Cursor(self.db_con.cursor(), self.db_con)
    except error:
      raise DatabaseError(error)

class Cursor:
  
  def __init__(self, db_cursor, db_con):
    self.db_cursor = db_cursor
    self.db_con = db_con
  
  def __getattr__(self, attr):
    # Redirect to underlying cursor
    return self.db_cursor.__getattribute__(attr)

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
      except error:
        raise ProgrammingError(error)

    sql = None

  
    # Convert IQL
    try:
      sql = iqlc.convert(operation, db_con.config)
    except iqlc.IQLTranslationError as error:
      raise ProgrammingError(error)
    except error:
      raise ProgrammingError(error)

    # Pass SQL to underlying cursor
    try:
      self.db_cursor.execute(sql)
    except error:
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
    except error:
      raise DatabaseError(error)

  def fetchmany(self, size = 4096):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.fetchmany(size = size)
    except error:
      raise DatabaseError(error)

  def fetchall(self):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.fetchall()
    except error:
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
    except error:
      raise DatabaseError(error)

  def setoutputsize(self, size, *columns):
    # Redirect to underlying cursor
    try:
      return self.db_cursor.setoutputsize(size, *columns)
    except error:
      raise DatabaseError(error)
