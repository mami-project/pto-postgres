#
# Path Transparency Observatory
# Analysis Runtime
#
from enum import Enum

import iql.convert
import pgdb
import pg

class BaseAnalysisContext:
    """
    Base class of analysis contexts.
    Implements observation set creation.
    """

    def __init__(self, conn):
      self._conn = conn
      self._dbw = pg.DB(self._conn)

    def create_observation_set(self, name):
        with self._dbw as db:
            observation_set = db.insert("observation_set", name=name, state='in_progress')

        return ObservationSetWriter(self, observation_set.osid)

class RawAnalysisContext(BaseAnalysisContext):
    """
    Analysis context for RawAnalyzers. 
    Implements access to raw data in HDFS via Spark.
    """

    def __init__(self, conn, some_handle_to_spark):
        super().__init__(conn)
        self._spark = some_handle_to_spark

class ObservationAnalysisContext(BaseAnalysisContext):

    def __init__(self, conn):
        super().__init__(conn)

        # store connection to the database
        self._conn = conn
        
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
    in_progress = 1
    pending_review = 2
    public = 3
    permanent = 4
    deprecated = 5
   

class ObservationSetStateError(Exception):
    pass

class ObservationSetWriter:
    
    def __init__(self, context, set_id):
        self._context = context
        self.osid = osid
        self.state = ObservationSetState.in_progress

    def observe(self, start_time, end_time, path, condition, value=None):
        if self.state == ObservationSetState.in_progress:
            self._context._dbw.insert('observation', full_path=path, time_from=start, time_to=end, condition=condition, val_n=value, observation_set=self.osid)
        else:
            raise ObservationSetStateException()

    def complete(self):
        """
        Finish writing observations to this observation set
        """
        self._context._dbw.update(osid=self.osid, state='pending_review')
        self.state = ObservationSetState.pending_review


######## ^ ### | ###########
######## | ### | ###########
######## | ### | ###########
### sten |     | britram ### 
######## | ### | ###########
######## | ### | ###########
######## | ### V ###########

class RawAnalyzer:
    '''
    A RawAnalyzer's run() method is invoked once for each 
    raw input file the core decides the analyzer is interested.
    raw_input_reader is a buffer-like object from which bytes
    can be read. metadata_dict is a dictionary containing
    metadata associated with the file on upload.
    '''
    def run(self, raw_input_reader, metadata_dict):
        pass

    '''
    The core can ask a RawAnalyzer whether it cares about a (new)
    input file by passing it a metadata dictionary 
    (including campaign name and filetype in addition to metadata).
    this function returns True if its run() method can do something
    useful with the raw data, or False() otherwise.
    '''
    def interested(self, metadata_dict):
        pass

class ObservationAnalyzer:
    '''
    An ObservationAnalyzer is invoked once for each query result
    set the core decides the analyzer is interested in. Generally,
    this will be an IQL query limited to the set of observation
    sets the analyzer has not yet run over.
    ''' 

    def run(self, cursor_iterator):
        pass

    '''
    The core can ask an ObservationAnalyzer for an IQL query that returns
    rows its run() method can process. The core will periodically run this
    query, limiting it to the observation sets not yet processed by the
    analyzer.
    '''
    def iql_query(self):
        pass
