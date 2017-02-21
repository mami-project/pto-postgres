from pg import DB, escape_string

import os
import os.path
import sys
import hashlib

dbname = input('DBName? ')
prefix = input('Upload folder? ')

db = DB(dbname = dbname)

def sha1_file_hash(path, chunk_size = 8192):
  fobj = open(path, 'rb')

  md = hashlib.sha1()
  while True:
    chunk = fobj.read(chunk_size)
    if len(chunk) == 0:
      break
    md.update(chunk)

  fobj.close()

  return md.hexdigest()

sql = """
 SELECT filesystem_path, file_hash FROM uploads;
"""

sys.stdout.write('Querying uploads....\n');

dr = db.query(sql).dictresult()
for e in dr:
  #print(e)
  path = os.path.join(prefix, e['filesystem_path'])

  if "#" in path:
    continue #can't check seq files yet

  if not os.path.exists(path):
    sys.stderr.write('WARNING: ' + e['filesystem_path'] + ' does not exist on file system!\n')
    continue
  
  size = os.path.getsize(path)
  sys.stdout.write("sz := %d, file_hash(db):= %s, " % (size, e['file_hash']))

  file_hash_ = sha1_file_hash(path)

  sys.stdout.write("file_hash(fs) := %s\n" % file_hash_)

  if e['file_hash'] != file_hash_:
    sys.stderr.write('WARNING: ' + e['filesystem_path'] + ' file_hash mismatch!\n')
    continue

  sql = """
  UPDATE uploads SET metadata = jsonb_set(
    metadata,
    '{file_size}',
    '%d') WHERE filesystem_path = '%s';
  """ % (size, escape_string(e['filesystem_path']))

  db.query(sql);
