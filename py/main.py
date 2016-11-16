import iql.convert as iqlc
import pprint

DICT_EXPECTED_TYPES_ATTR = {
  'time_to' : 'T',
  'time_from' : 'T',
  'condition' : 'S',
  'path_id' : 'I',
  'dip' : 'S',
  'sip' : 'S',
  'full_path' : 'S',
  'path_id' : 'I',
  'analyzer' : 'S'
}

DICT_MSMNT_TYPES = {
  'ecn.connectivity' : 'S',
  'ecn.negotiated' : 'I'
}

config = iqlc.Config(msmnt_types = DICT_MSMNT_TYPES, expected_types = DICT_EXPECTED_TYPES_ATTR)


pp = pprint.PrettyPrinter(indent = 2)

#sieve = {"sieve":[{"eq":["$ecn.connectivity","works"]},{"eq":["$ecn.connectivity","broken"]}]}
#lookup = {"lookup" : ["","$ecn.connectivity", sieve]}
#query = {"settings" : {"order" : ["$ecn.connectivity","asc"]}, "query":{"all": [lookup]}}

#query = {"query" : {"all" : [{"simple":[{"or":[{"eq":["$ecn.connectivity","works"]},{"eq":["$ecn.negotiated",1]}]}]}]}}

qpart = {"simple" : [{"choice": [ {"eq": ["$ecn.connectivity","works"]},
                                  {"eq": ["$ecn.negotiated", 1]}]}]}

query = {"query":{"all":[qpart]}}

print("[ IQL ]\n")

pp.pprint(query)
print("")
print(query)

print("")

sql = iqlc.convert(query, config = config)

print("[ SQL ]\n")

print(sql)
