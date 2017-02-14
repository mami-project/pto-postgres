#
# Path Transparency Observatory
# Analysis Runtime
#
from enum import Enum

import collections
from datetime import datetime
import iql.convert
import pg
import pgdb

class BaseAnalysisContext:
    """
    Base class of analysis contexts.
    Implements observation set creation.
    """

    def __init__(self, db):
      self._db = db

    def create_observation_set(self, name):
        with self._db as db:
            observation_set = db.insert("observation_set", name=name, state='in_progress')
        print(observation_set)
        return ObservationSetWriter(self, observation_set['osid'])

class RawAnalysisContext(BaseAnalysisContext):
    """
    Analysis context for RawAnalyzers. 
    Implements access to raw data in HDFS via Spark.
    """

    def __init__(self, db):
        super().__init__(db)

class ObservationAnalysisContext(BaseAnalysisContext):

    def __init__(self, db):
        super().__init__(db)
        
    def iql_query(self, iql_ast):
        """
        execute an IQL query, return an iterator over the result
        """

        # turn IQL into SQL
        sql = iql.convert.convert(iql_ast)

        # create a cursor and execute the query
        c = self._conn.cursor()
        c.execute(sql)

        # wrap the cursor in an iterator
        return CursorIterator(c)

class CursorIterator:

    def __init__(self, c):
        # execute the IQL query, store the cursor
        self._c = c

    def __iter__(self):
        row = self._c.fetchone()
        if row is None:
            raise StopIteration
        else:
            return row


class ObservationSetState(Enum):
    """
    State information for an observation set. Members must have the same
    spelling (including capitalisation) as the SQL type os_state described
    in iql_minimal.sql.
    """
    unknown = 'unknown'
    in_progress = 'in_progress'
    pending_review = 'pending_review'
    public = 'public'
    permanent = 'permanent'
    deprecated = 'deprecated'
   

class ObservationSetStateError(Exception):
    def __init__(self, observed_state, expected_state):
        self.observed_state = observed_state
        self.expected_state = expected_state

    def __str__(self):
        return 'Observed state {0:s}, expected {1:s}'.format(self.observed_state, self.expected_state)

class ObservationSetNotFoundError(Exception):
    def __init__(self, param):
        self.param = param

class DuplicateConditionError(Exception):
    def __init__(self, full_name):
        self.full_name = full_name

class ConditionTypeError(Exception):
    def __init__(self, specified, found):
        self.specified = specified
        self.found = found

def timestamp_str(ts):
    if ts is None:
        return 'never'
    else:
        return ts.__str__()

def revision_id_string(revid):
    if revid is None:
        return 'never'
    else:
        return str(revid)

def metadata_to_string(md):
    if md is None:
        return ''
    else:
        return md.__str__()

class ObservationSet:
    def __init__(self, db):
        self._db = db
        self._state = ObservationSetState.unknown

    def load(self, osid):
        self._load(osid)

    def create(self, name, metadata):
        self._create(name, metadata)

    def __str__(self):
        if self._state == ObservationSetState.unknown:
            return 'OSID unknown'
        else:
            roc = revision_id_string(self._roc)
            rov = revision_id_string(self._rov)
            rod = revision_id_string(self._rod)
            md = metadata_to_string(self._metadata)
            return 'OSID {2:d} \'{0:s}\', {1:s}, roc {3:s}, rov {4:s}, rod {5:s} {6:s}' \
                .format(self.name, self._state.name, self.osid, roc, rov, rod, md)

    @staticmethod
    def find_sets_by_name(db, name):
        '''
        Retrieves all observation sets for a given name. Not the most
        efficient implementation, but should work
        '''
        ret = list()
        with db as d:
            observation_sets = d.query('SELECT * FROM observation_set WHERE name = $1', name)
        if observation_sets is not None:
            for observation_set in observation_sets.dictresult():
                new_o = ObservationSet(db)
                # Does a redundant trip to the database. May be a performance problem.
                new_o.load(observation_set['osid'])
                ret.append(new_o)
            return ret
        else:
            raise ObservationSetNotFoundError(name)

    @staticmethod
    def find_latest_unfinished_set(db, name):
        '''
        Retrieves the latest (highest revision for creation, roc) observation set
        for a given analyzer name that is still in progress. May return None if
        there is no such set, i.e., either the analyzer name doesn't exist or
        none of the observation sets with that analyzer name are in_progress.
        '''
        with db as d:
            ret = d.query('SELECT * FROM observation_set WHERE roc = (SELECT MAX(roc) FROM observation_set WHERE name = $1 AND state = $2)', name, ObservationSetState.in_progress.name)
        if ret is not None:
            new_o = ObservationSet(db)
            # Makes a redundant trip to the database. May be a performance problem.
            new_o.load(ret['osid'])
            return new_o
        else:
            return None

    def _create_revid(self, db, name):
        '''
        Creates a new revision ID.
        '''
        return db.insert('observation_set_revision', creator=name)

    def _create(self, name, metadata=None):
        '''
        Creates a new observation set with a new, unised observation set ID
        '''
        with self._db as db:
            revid = self._create_revid(db, name)
            observation_set = db.insert('observation_set', name=name,
                state=ObservationSetState.in_progress.name,
                roc=revid['revision'])

            self.osid = observation_set['osid']
            self.name = observation_set['name']
            self._state = ObservationSetState(observation_set['state'])
            self._roc = observation_set['roc']
            self._rov = observation_set['rov'] # None
            self._rod = observation_set['rod'] # None

            self._metadata = metadata
            if metadata is not None:
                for key in metadata:
                    db.insert('observation_set_metadata', osid=self.osid,
                        key=key, value=metadata[key])

    def _load(self, osid):
        with self._db as db:
            observation_set = db.get('observation_set', osid, 'osid')
        if observation_set is not None:
            self.osid = observation_set['osid']
            self.name = observation_set['name']
            self._state = ObservationSetState(observation_set['state'])
            self._roc = observation_set['roc']
            self._rov = observation_set['rov']
            self._rod = observation_set['rod']

            self._metadata = dict()
            with self._db as db:
                metadata = db.query('SELECT * from observation_set_metadata WHERE osid = $1', self.osid).getresult()
            for m in metadata:
                self._metadata[m[1]] = m[2]
        else:
            raise ObservationSetNotFoundError(osid)

    def resume(self, osid):
        '''
        Loads an existing observation set, given its observation set ID.
        Raises an ObservationSetNotFoundError if the observation set ID does
        not exist, raises an ObservationSetStateError if the observation
        set is not in state in_progress.
        '''
        self._load(osid)
        if self._state != ObservationSetState.in_progress:
            raise ObservationSetStateError(self._state, ObservationSetState.in_progress)

    def commit(self):
        '''
        Makes this observation set available to review. Raises an
        ObservationSetStateError of the state is not in_progress.
        '''
        if self._state != ObservationSetState.in_progress:
            raise ObservationSetStateError(self._state, ObservationSetState.in_progress)

        with self._db as db:
            self._state = ObservationSetState.pending_review            
            db.update('observation_set', osid=self.osid, state=self._state.name)

    def publish(self):
        '''
        Makes this observation set available for analysers.  Raises an
        ObservationSetStateError if the state is not pending_review.

        TODO: Do we need another revision ID for this state transition?
        '''
        if self._state != ObservationSetState.pending_review:
            raise ObservationSetStateError(self._state, ObservationSetState.pending_review)

        with self._db as db:
            revid = self._create_revid(db, self.name)
            self._state = ObservationSetState.public
            self._rov = revid['revision']
            db.update('observation_set', osid=self.osid, state=self._state.name, rov=self._rov)

    def make_permanent(self):
        '''
        Makes this observation set permanent.  Raises an
        ObservationSetStateError if the state is not public.

        TODO: Do we need another revision ID for this state transition?
        '''
        if self._state != ObservationSetState.public:
            raise ObservationSetStateError(self._state, ObservationSetState.public)

        with self._db as db:
            self._state = ObservationSetState.permanent
            db.update('observation_set', osid=self.osid, state=self._state.name)

    def deprecate(self):
        '''
        Makes this observation set deprecated.  Raises an
        ObservationSetStateError if the state is not permanent.
        '''
        if self._state != ObservationSetState.permanent:
            raise ObservationSetStateError(self._state, ObservationSetState.permanent)

        with self._db as db:
            revid = self._create_revid(db, self.name)
            self._state = ObservationSetState.deprecated
            self._rod = revid['revision']
            db.update('observation_set', osid=self.osid, state=self._state.name, rod=self._rod)

    def is_being_worked_on(self):
        return self._state == ObservationSetState.in_progress

    def is_review_pending(self):
        return self._state == ObservationSetState.pending_review

    def is_published(self):
        return self._state == ObservationSetState.public

    def is_permanent(self):
        return self._state == ObservationSetState.permanent

    def is_deprecated(self):
        return self._state == ObservationSetState.deprecated

    def can_delete(self):
        return self._state == ObservationSetState.in_progress \
            or self._state == ObservationSetState.pending_review \
            or self._state == ObservationSetState.public


def get_condition_by_full_name(db, full_name):
    with db as db:
        return db.query('SELECT * FROM condition_tree WHERE full_name = $1', full_name).getresult()

class Condition:
    def __init__(self, db, full_name, ctype='N'):
        self._db = db
        self.full_name = full_name
        self.ctype = ctype
        self._load_or_create()

    def __str__(self):
        return 'Condition {0:d} full name {1:s}'.format(self.cid, self.full_name)

    def _load_or_create(self):
        conditions = get_condition_by_full_name(self._db, self.full_name)
        if len(conditions) > 1:
            raise DuplicateConditionError(self.full_name)
        elif len(conditions) == 1:
            self.cid = conditions[0][0]
            if conditions[0][2] != self.ctype:
                raise ConditionTypeError(self.ctype, conditions[0][2])
        else:
            assert len(conditions) == 0
            full_name = None
            parent = None
            for name in self.full_name.split('.'):
                if full_name is None:
                    full_name = name
                else:
                    full_name = full_name + '.' + name
                conditions = get_condition_by_full_name(self._db, full_name)
                if len(conditions) == 0:
                    with self._db as db:
                        if parent is None:
                            new_condition = db.insert('condition_tree', name=name, full_name=full_name)
                        else:
                            new_condition = db.insert('condition_tree', name=name, full_name=full_name, parent=parent)
                        if self.full_name == full_name:
                            db.update('condition_tree', full_name=full_name, type=self.ctype)
                    parent = new_condition['cid']
                elif len(conditions) == 1:
                    parent = conditions[0][0]
                else:
                    raise DuplicateConditionError(self.full_name)
            self.cid = parent
            assert self.cid is not None

class ObservationSetWriter:
    def __init__(self, db, name, set_id=None):
        self._db = db
        self.name = name
        self._observation_set = ObservationSet(db)
        if set_id is None:
            self._observation_set.create(self.name, None)
        else:
            self._observation_set.resume(set_id)

    def begin(self, name=None):
        pass

    def commit(self):
        self.complete()

    def observe(self, time_from, time_to, path, condition, value=None):
        # This method call may be a performance bottleneck. If it is, one
        # needs to make ObservationSet._state public, and remove the is_...
        # functions from ObservationSet.
        if self._observation_set.is_being_worked_on():
            self._db.insert('observation', full_path=path, time_from=time_from, time_to=time_to, condition=condition, val_n=value, observation_set=self._observation_set.osid)
        else:
            raise ObservationSetStateException(self._state, ObservationSetState.in_progress)

    def complete(self):
        """
        Finish writing observations to this observation set
        """
        self._observation_set.commit()


######## ^ ### | ###########
######## | ### | ###########
######## | ### | ###########
### sten |     | britram ### 
######## | ### | ###########
######## | ### | ###########
######## | ### V ###########

#
# Analysis Runtime MPI definition
#

Observation = collections.namedtuple("Observation", ("start_time", "end_time", "path", "condition", "value", "observation_set"))

class RawAnalyzer:
    '''
    Interface definition for RawAnalyzer. A RawAnalyzer analyzes
    raw measurement data and creates observations.

    Any object that implements appropriate run() and interested() 
    methods may be used as a RawAnalyzer.
    '''

    def run(self, reader, writer, metadata):
        '''
        A RawAnalyzer's run() method is invoked once for each 
        raw input file the analyzer is interested in.
        The run() method should analyze the input file completely,
        writing observations to the supplied writer.

        :param reader: is a binary or text file object open for reading,
        depending on the filetype of the underlying file.

        :param writer: is an ObservationSetWriter to write observations to.

        :param dict metadata: metadata associated 
        with the file on upload. FIXME: which keys are guaranteed?
        '''
        raise NotImplementedError("cannot instantiate abstract RawAnalyzer")

    def interested(self, metadata):
        '''
        A RawAnalyzer's interested() method is invoked with the metadata
        for a newly uploaded file. It should return True if the metadata
        represents a file the analyzer can analyze.

        :param dict metadata: metadata associated 
        with the file on upload. FIXME: which keys are guaranteed?

        :rtype bool:
        '''
        raise NotImplementedError("cannot instantiate abstract RawAnalyzer")

class ObservationSetAnalyzer:
    '''
    Interface definition for ObservationSetAnalyzer. 
    An ObservationSetAnalyzer analyzes observations on a 
    per-observation set basis, and derives observations from them.

    Any object that implements appropriate run() and interested() 
    methods may be used as an ObservationSetAnalyzer.

    ''' 

    def run(self, observations, writer):
        '''
        An ObservationSetAnalyzer's run() method is invoked once for each 
        observation set the analyzer is interested in.

        The run() method should analyze the observation set
        completely, writing derived observations to the supplied writer.

        :param observations: is an iterator over all the Observations in
        the (one or more) ObservationSets included in this run.

        :param writer: is an ObservationSetWriter to write observations to.
        '''
        raise NotImplementedError("cannot instantiate abstract ObservationSetAnalyzer")

    def interested(self, conditions, metadata):
        '''
        An ObservationSetAnalyzer's interested() method is invoked 
        with a set of conditions (as strings) available in a given
        observation set. It should return True if the conditions
        represent an observation set the analyzer can analyze.

        :param set conditions: conditions present in the observation set

        :param dict metadata: observation set metadata


        :rtype: bool
        '''
        raise NotImplementedError("cannot instantiate abstract ObservationSetAnalyzer")

class QueryAnalyzer:
    '''
    Interface definition for QueryAnalyzer. A QueryAnalyzer
    runs one or more arbitrary IQL queries when invoked, and
    derives observations from them.

    Any object that implements an appropriate run() method
    may be used as a QueryAnalyzer.
    '''

    def run(self, query_context, writer, **kwargs):
        '''
        A QueryAnalyzer's run() method is invoked externally; it takes
        additional keyword arguments specified by its invocation
        environment. The run() method should use the query_context to
        run an arbitrary IQL query against the database, writing
        derived observations to a supplied writer.

        :param query_context: wraps a database connection; it provides a single 
        iql_query method to run queries against the database.

        :param writer: is a ObservationSetWriter to write observations to.
        '''
        raise NotImplementedError("cannot instantiate abstract QueryAnalyzer")

