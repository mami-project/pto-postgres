from arun import ObservationSetWriter, Condition, ObservationSetState, ObservationSetStateError, RawAnalysisContext, ObservationSet
from pg import DB
import pgdb

db = DB(dbname='pto', host='localhost', port=5432,
	user='sten', passwd='sten')

os1 = ObservationSet(db)
os1.create('O RLY', { 'test' : 'one', 'other test' : 'two'})

try:
	# Raises ObservationSetStateError
	os1.make_permanent()
	assert False
except ObservationSetStateError as e:
	print(e)
	assert e.observed_state == ObservationSetState.in_progress \
		and e.expected_state == ObservationSetState.public

# Writes new state to database
os1.commit()

os2 = ObservationSet(db)
os2.load(os1.osid())

print(os1)
print(os2)

assert os1.is_review_pending() and os2.is_review_pending()

os1.publish()
os1.make_permanent()
os1.deprecate()

print('Observation set 1: {0:s}'.format(os1.__str__()))

os1 = ObservationSet(db)
os1.create('O RLY 1', None)

sets = ObservationSet.find_sets_by_name(db, 'O RLY')
for set in sets:
	print(set)
sets = ObservationSet.find_sets_by_name(db, 'O RLY 1')
for set in sets:
	print(set)

c = Condition(db, 'ecn.connectivity.works')
print(c)

c = Condition(db, 'ecn.connectivity.super.works')
print(c)

c = Condition(db, 'some.new.connectivity.super.works')
print(c)

#ctx = RawAnalysisContext(db)
#obset = ctx.create_observation_set("huba-huba")

#time_from = pgdb.Timestamp(2017, 2, 2, 10)
#time_to = pgdb.Timestamp(2017, 2, 2, 11)
#path = "* - *"
#condition = 2

#obset.observe(time_from, time_to, path, condition)
#obset.complete()