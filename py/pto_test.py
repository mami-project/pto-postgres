from arun import ObservationSetWriter, ObservationSetState, RawAnalysisContext, ObservationSet
from pg import DB
import pgdb

db = DB(dbname='pto', host='localhost', port=5432,
	user='sten', passwd='sten')

os = ObservationSet(db)

os.create('O RLY')

os.state = ObservationSetState.permanent

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