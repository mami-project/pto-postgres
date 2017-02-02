import sys
from collections import OrderedDict

class Tests():

  @staticmethod
  def test_const_true(cursor):
    pass


  @staticmethod
  def dict_compare(expected, got):

    for key in expected:
      if not key in got: return (False, '!' + key)

    for key in expected:
      if not Tests.equ(expected[key], got[key]): return (False, key)

    return (True, None)

  @staticmethod
  def equ(a, b):

    if type(a) != type(b): 
      return False

    if type(a) == type([]):
      if len(a) != len(b): return False
      i = 0
      while i < len(a):
        if not Tests.equ(a[i], b[i]): 
          return False
        i += 1

      return True

    else:
      return a == b

    raise Exception('Should not happen!')


  @staticmethod
  def check_dict_compare(expected, got):
    (ret, key) = Tests.dict_compare(expected, got)
    if not ret:
      msg = ('Expected %s' % str(expected))
      msg += (' but got %s' % str(got))
      msg += (' Offending key was %s' % str(key))
      raise Exception(msg)
    return ret


  @staticmethod
  def check_one(cursor, iql, expected):
    cursor.execute(iql)
    result = cursor.fetchone()
    
    return Tests.check_dict_compare(expected, result)
    

  @staticmethod
  def check_len(rows, expected_len):
    if len(rows) != expected_len:
      raise Exception('Expected len %d but got %d for %s' % (expected_len, len(rows), str(rows)))


  @staticmethod
  def test_find_msmnt(cursor):
    iql = {"query" : {"all" : [{"simple" : [{"eq":["@name","msmnt3"]}]}]}}
    expected = {"oid":5.0, "name" : "msmnt3", "value" : 1.0, "attr_a" : 3.5}

    Tests.check_one(cursor, iql, expected)


  @staticmethod
  def test_intersection(cursor):
    iql = {"query" : {"all" : [{"intersection" : [
            {"simple":[{"eq":["@name","msmnt1"]}]},
            {"simple":[{"eq":["@name","msmnt2"]}]}
          ]}]}, "settings":{"attribute":"@attr_b"}}

    expected = {"attr_b" : ["a","b","c"]}

    cursor.execute(iql)
    rows = cursor.fetchall()
    
    Tests.check_len(rows, 1)
    Tests.check_dict_compare(expected, rows[0])


  @staticmethod
  def test_subtraction(cursor):
    iql = {"query" : {"all" : [{"subtraction" : [
            {"simple":[{"eq":["@name","msmnt1"]}]},
            {"simple":[{"eq":["@name","msmnt2"]}]}
          ]}]}, "settings":{"attribute":"@attr_b"}}

    expected = {"attr_b" : ["l","m","n"]}

    cursor.execute(iql)
    rows = cursor.fetchall()
    
    Tests.check_len(rows, 1)
    Tests.check_dict_compare(expected, rows[0])


  @staticmethod
  def test_sieve(cursor):
    iql = {"query" : {"all" : [{"sieve" : [
            {"eq":["@name","msmnt5"]},
            {"eq":["$msmnt5:1",{"mul":[2,"$msmnt5:0"]}]}
          ]}]}, "settings":{"attribute":"@attr_b"}}

    expected = {"attr_b" : ["u","m","g"]}

    cursor.execute(iql)
    rows = cursor.fetchall()
    
    Tests.check_len(rows, 1)
    Tests.check_dict_compare(expected, rows[0])


if len(sys.argv) != 2:
  print('Need path!')
  exit()

sys.path.append(sys.argv[1])


import iql.db as iqld
from iql.convert import Config

def main():
  dbname = input('DB? ')
  user = input('User? ')
  password = input('Password? ')

  if(dbname == None or dbname == ""): dbname = "pto"
  if(user == None or user == ""): user = "mroman"
  if(password == None or password == ""): password = "foobar"

  config = Config(tbl_name = 'iql_test', 
                  expected_types = {"name" : "S", "attr_a" : "N", "attr_b" : "*S"}, 
                  msmnt_types = {'msmnt1' : 'N', 'msmnt2' : 'N', 'msmnt3' : 'N', 'msmnt4' : 'N', 'msmnt5' : 'N'})


  con = iqld.pg_connect(database = dbname, user = user, password = password, config = config)

  for method in dir(Tests):
    if method.startswith('test_'):
      print('Invoking %s' % method)
      cursor = con.cursor()
      result = getattr(Tests, method)(cursor)
      cursor.close()

if __name__ == "__main__": main()
