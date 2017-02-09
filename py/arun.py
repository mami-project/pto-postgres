#
# Path Transparency Observatory
# Analysis Runtime
#
from enum import Enum

import iql.convert
import pg

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
    unknown = 1
    in_progress = 2
    pending_review = 3
    public = 4
    permanent = 5
    deprecated = 6
   

class ObservationSetStateError(Exception):
    def __init__(self, observed_state, expected_state):
        self.observed_state = observed_state
        self.expected_state = expected_state

class ObservationSetNotFoundError(Exception):
    def __init__(self, param):
        self.param = param

class ObservationSet:
    # TODO Make this subscriptable
    def __init__(self, db):
        self._db = db
        self._state = ObservationSetState.unknown

    def __str__(self):
        if self._state == ObservationSetState.unknown:
            return 'OSID unknown'
        else:
            if self._toi is None:
                toi = 'never'
            else:
                toi = self._toi.__str__()

            return 'OSID {2:d} \'{0:s}\', {1:s}, created {3:s}, invalidated {4:s}'\
                .format(self._name, self._state, self._osid, self._toc.__str__(), toi)

    @property
    def state(self):
        '''The state of this observation set'''
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        print(self._state)
        with self._db as db:
            db.update('observation_set', osid=self._osid, state=self._state.name)

    @state.deleter
    def state(self):
        pass

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
                o = ObservationSet(db)
                o.resume(observation_set['osid'])
                ret.append(o)
            return ret
        else:
            raise ObservationSetNotFoundError(name)

    def create(self, name, metadata=None):
        '''
        Creates a new observation set with a new, unised observation set ID
        '''
        with self._db as db:
            print(ObservationSetState.in_progress)
            observation_set = db.insert('observation_set', name=name,
                state=ObservationSetState.in_progress.name)
            self._state = observation_set['state']
            self._osid = observation_set['osid']
            self._toc = observation_set['toc']
            self._name = observation_set['name']
            self._toi = observation_set['toi']
            self._metadata = metadata
        if metadata is not None:
            with self._db as db:
                for key in metadata:
                    db.insert('observation_set_metadata', osid=self._osid,
                        key=key, value=metadata[key])

    def resume(self, osid):
        '''
        Loads an existing observation set, given its observation set ID.
        Raises an ObservationSetNotFoundError if the observation set ID does
        not exist
        '''
        with self._db as db:
            observation_set = db.get('observation_set', osid, 'osid')
        if observation_set is not None:
            self._state = observation_set['state']
            self._osid = observation_set['osid']
            self._toc = observation_set['toc']
            self._name = observation_set['name']
            self._toi = observation_set['toi']
            self._metadata = dict()
            with self._db as db:
                metadata = db.query('SELECT * from observation_set_metadata WHERE osid = $1', self._osid).getresult()
            for m in metadata:
                self._metadata[m[0]] = m[1]
        else:
            raise ObservationSetNotFoundError(osid)

class ObservationSetWriter:
    def __init__(self, db, name, set_id=None):
        self._db = db
        self._name = name
        if set_id is not None:
            self._set_id = set_id
            self.resume(set_id)
        else:
            pass

    def resume(self, set_id):
        pass


    def begin(self, name=None):
        pass

    def commit(self):
        self.complete()

    def observe(self, time_from, time_to, path, condition, value=None):
        if self._state == ObservationSetState.in_progress:
            self._context._dbw.insert('observation', full_path=path, time_from=time_from, time_to=time_to, condition=condition, val_n=value, observation_set=self._set_id)
        else:
            raise ObservationSetStateException(self._state, ObservationSetState.in_progress)

    def complete(self):
        """
        Finish writing observations to this observation set
        """
        if self._state == ObservationSetState.in_progress:
            self._context._dbw.update(osid=self._set_id, state='pending_review')
            self._state = ObservationSetState.pending_review
        else:
            raise ObservationSetStateException(self.state, ObservationSetState.in_progress)


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

#Observation = collections.namedtuple("Observation", ("start_time", "end_time", "path", "condition", "value"))

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

        reader is a binary or text file object open for reading,
        depending on the filetype of the underlying file.

        writer is an ObservationSetWriter to write observations to.

        metadata is a dict, containing metadata associated 
        with the file on upload. FIXME: which keys are guaranteed?
        '''
        raise NotImplementedError("cannot instantiate abstract RawAnalyzer")

    def interested(self, metadata):
        '''
        A RawAnalyzer's interested() method is invoked with the metadata
        for a newly uploaded file. It should return True if the metadata
        represents a file the analyzer can analyze.
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

        observations is an iterator of Observations, such that every 
        observation belongs to the same observation set.

        writer is an ObservationSetWriter to write observations to.
        '''
        raise NotImplementedError("cannot instantiate abstract ObservationSetAnalyzer")

    def interested(self, conditions):
        '''
        An ObservationSetAnalyzer's interested() method is invoked 
        with a set of conditions (as strings) available in a given
        observation set. It should return True if the conditions
        represent an observation set the analyzer can analyze.
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

        query_context wraps a database connection; it provides a single 
        iql_query method to run queries against the database.

        writer is a ObservationSetWriter to write observations to.
        '''
        raise NotImplementedError("cannot instantiate abstract ObservationSetAnalyzer")

