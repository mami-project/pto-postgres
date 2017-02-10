from arun import ObservationSetWriter, ObservationSetState, RawAnalysisContext, ObservationSet
from pg import DB
import pgdb

db = DB(dbname='pto', host='localhost', port=5432,
	user='sten', passwd='sten')

os = ObservationSet(db)

# Create a new observation set with the given name
os.create('O RLY')

# This will persist the observation set
os.state = ObservationSetState.permanent

# Test deprecation
os.create('O RLY')
os.state = ObservationSetState.deprecated

sets = ObservationSet.find_sets_by_name(db, 'O RLY')
for set in sets:
	print(set)
#ctx = RawAnalysisContext(db)
#obset = ctx.create_observation_set("huba-huba")

#time_from = pgdb.Timestamp(2017, 2, 2, 10)
#time_to = pgdb.Timestamp(2017, 2, 2, 11)
#path = "* - *"
#condition = 2

#obset.observe(time_from, time_to, path, condition)
#obset.complete()