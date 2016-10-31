import bson
import datetime

f = open('observations1.bson','rb')
it = bson.decode_file_iter(f)
i = 0

paths = {}
lastPathId=1
lastObservationId=1
lastValueId=1
lastNodeId=1
nodes = {}
analyzers = {'analyzer-ecnspider1' : 1, 'analyzer-ecnspider1-vp' : 2}
lastObservationId=1

print("-- BEGIN")

for (key, value) in analyzers.items():
  print("INSERT INTO ANALYZER(ID, NAME) VALUES(%d, '%s');" % (value, key))
  

for doc in it:
  path = doc['path']
  analyzer = doc['analyzer_id']

  if analyzer not in analyzers:
    print('-- WARNING: Unknown analyzer' + analyzer)

  analyzerId = analyzers[analyzer]

  fullPath = ' - '.join(path)

  pathId = lastPathId

  if (i % 1000) == 0:
    print("BEGIN;")

  # 
  # Create path if necessary.
  #
  if(fullPath in paths):
    pathId = paths[fullPath]
    print('-- ' + fullPath + ' exists id = ' + str(pathId))
  else:
    paths[fullPath] = pathId
    lastPathId += 1

    # Create path first
    sql = "INSERT INTO PATH(ID, FULL_PATH, SIP, DIP) VALUES(%d, '%s', '%s', '%s');"
    print(sql % (pathId, fullPath, path[0], path[-1]))

    # Create nodes
    pos = 0
    for node in path:
      nodeId = lastNodeId
      if node in nodes:
        nodeId = nodes[node]
        print('-- ' + node + ' exists id = ' + str(nodeId))
      else:
        nodes[node] = nodeId
        lastNodeId += 1

        # Create node
        sql = "INSERT INTO NODE(ID, NAME) VALUES(%d,'%s');"
        print(sql % (nodeId, node))

      # Create path_node
      sql = "INSERT INTO PATH_NODE(PATH_ID, NODE_ID, POS) VALUES(%d, %d, %d);"
      print(sql % (pathId, nodeId, pos))
      
      pos += 1

  # Create observations
  t_from = doc['time']['from'].isoformat()
  t_to = doc['time']['to'].isoformat()

  
  

  for condition in doc['conditions']:
    obsId = lastObservationId
    lastObservationId += 1    

    sql = None
    if(condition == "ecn.negotiated"):
      condition = "ecn.negotiated"
      sql = "INSERT INTO OBSERVATION(ID, PATH_ID, ANALYZER_ID, TIME_FROM, TIME_TO, CONDITION, VAL_I) VALUES(%d, %d, %d, '%s','%s', '%s', %d);" % (obsId, pathId, analyzerId, t_from, t_to, condition, 1)
    elif(condition == "ecn.not_negotiated"):
      condition = "ecn.negotiated"
      sql = "INSERT INTO OBSERVATION(ID, PATH_ID, ANALYZER_ID, TIME_FROM, TIME_TO, CONDITION, VAL_I) VALUES(%d, %d, %d, '%s','%s', '%s', %d);" % (obsId, pathId, analyzerId, t_from, t_to, condition, 0)
    elif(condition.startswith("ecn.connectivity.")):
      value = condition[17:]
      condition = "ecn.connectivity"
      sql = "INSERT INTO OBSERVATION(ID, PATH_ID, ANALYZER_ID, TIME_FROM, TIME_TO, CONDITION, VAL_S) VALUES(%d, %d, %d, '%s','%s', '%s', '%s');" % (obsId, pathId, analyzerId, t_from, t_to, condition, value)

    print(sql)

  if (i % 1000) == 999:
    print("COMMIT;")
  
  i += 1
  if(i > 1000000):
    break

print("COMMIT;")
print("-- END")

