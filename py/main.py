import iql.convert as iqlc
import pprint




pp = pprint.PrettyPrinter(indent = 2)

#sieve = {"sieve":[{"eq":["$ecn.connectivity","works"]},{"eq":["$ecn.connectivity","broken"]}]}
#lookup = {"lookup" : ["","$ecn.connectivity", sieve]}
#query = {"settings" : {"order" : ["$ecn.connectivity","asc"]}, "query":{"all": [lookup]}}

query = {"query" : {"count" : [["@dip","$ecn.connectivity"],{"simple":[{"eq":[1,1]}]}]}}

print("[ IQL ]\n")

pp.pprint(query)
print("")
print(query)

print("")

sql = iqlc.convert(query)

print("[ SQL ]\n")

print(sql)
