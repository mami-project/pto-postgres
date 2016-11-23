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
analyzers = {'analyzer-ecnspider1' : 1, 'analyzer-ecnspider-vp' : 2}
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
    #print('-- ' + fullPath + ' exists id = ' + str(pathId))
  else:
    paths[fullPath] = pathId
    lastPathId += 1

    # Create path first
    sql = "INSERT INTO PATH(ID, FULL_PATH, SIP, DIP) VALUES(%d, '%s', '%s', '%s');"
    print(sql % (pathId, fullPath, path[0], path[-1]))

    node_values = []
    path_node_values = []

    # Create nodes
    pos = 0
    for node in path:
      nodeId = lastNodeId
      if node in nodes:
        nodeId = nodes[node]
        #print('-- ' + node + ' exists id = ' + str(nodeId))
      else:
        nodes[node] = nodeId
        lastNodeId += 1

        # Create node
        node_values.append("(%d,'%s')" % (nodeId, node))

      # Create path_node
      path_node_values.append("(%d,%d,%d)" % (pathId, nodeId, pos))
      
      pos += 1

    if len(node_values) > 0:
      print("INSERT INTO NODE(ID,NAME) VALUES %s;" % (",".join(node_values)))

    if len(path_node_values) > 0:
      print("INSERT INTO PATH_NODE(PATH_ID,NODE_ID,POS) VALUES %s;" % (",".join(path_node_values)))

  # Create observations
  t_from = doc['time']['from'].isoformat()
  t_to = doc['time']['to'].isoformat()

  
  observation_values = []

  for condition in doc['conditions']:
    obsId = lastObservationId
    lastObservationId += 1    

    

    sql = None
    if(condition == "ecn.negotiated"):
      condition = "ecn.negotiated"
      observation_values.append("(%d,%d,%d,'%s','%s','%s',%d,NULL,NULL,NULL)" % (obsId, pathId, analyzerId, t_from, t_to, condition, 1))
    elif(condition == "ecn.not_negotiated"):
      condition = "ecn.negotiated"
      observation_values.append("(%d,%d,%d,'%s','%s','%s',%d,NULL,NULL,NULL)" % (obsId, pathId, analyzerId, t_from, t_to, condition, 0))
    elif(condition.startswith("ecn.connectivity.")):
      value = condition[17:]
      condition = "ecn.connectivity"
      observation_values.append("(%d,%d,%d,'%s','%s','%s',NULL,'%s',NULL, NULL)" % (obsId, pathId, analyzerId, t_from, t_to, condition, value))
    elif condition == "ecn.path_dependent" or condition == "ecn.site_dependent":
      value = list(map(lambda a: "'%s'" % a, doc['value']['sips']))
      observation_values.append("(%d,%d,%d,'%s','%s','%s',NULL,NULL,ARRAY[%s]::VARCHAR[], NULL)" % (obsId, pathId, analyzerId, t_from, t_to, condition, ",".join(value)))

  print("INSERT INTO OBSERVATION(ID,PATH_ID,ANALYZER_ID,TIME_FROM,TIME_TO,CONDITION,VAL_N,VAL_S,VAL_A_S,VAL_A_N) VALUES %s;" % (",".join(observation_values)))

  if (i % 1000) == 999:
    print("COMMIT;")
  
  i += 1
  #if(i > 1000000):
  #  break

print("COMMIT;")
print("-- END")

