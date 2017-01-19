#
# Path Transparency Observatory
# Analysis Runtime
#

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
        obset = self._dbw.insert("observation", name=name)
        return ObservationSetWriter(self, obset.id)

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


class ObservationSetWriter:
    
    def __init__(self, context, set_id):
        self._context = context
        self.osid = osid

    def observe(self, start_time, end_time, path, condition, value=None):
        self.context._dbw.insert('observation', full_path=path, time_from=start, time_to=end, condition=condition, val_n=value, observation_set=self.osid)

    def complete(self):
        """
        Finish writing observations to this observation set
        """
        pass

class RawAnalyzer:
    def run(self, context):
        pass

class ObservationAnalyzer:
    def run(self, context):
        pass
