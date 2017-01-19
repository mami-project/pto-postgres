#
# Path Transparency Observatory
# Analysis Runtime
#

import iql.convert

class BaseAnalysisContext:
    """
    Base class of analysis contexts.
    Implements observation set creation.
    """

    def __init__(self, conn):
        self._conn = conn

    def create_observation_set(self):
        pass


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
        cursor = self._conn.cursor()
        cursor.execute(sql)

        # wrap the cursor in an iterator
        return CursorIterator(cursor)

class CursorIterator:

    def __init__(self, cursor):
        # execute the IQL query, store the cursor
        self._c = cursor

    def __iter__(self):
        row = self._c.fetchone()
        if row is None:
            raise StopIteration
        else:
            return row


class ObservationSetWriter:

    def observe(self, start, end, path, condition, value):
        pass

    def complete(self):
        """
        Finish writing observations to this observation set
        """
        pass




class ObservationSetReader:

    def __init__(self):


    def __iter__(self):
        """
        Iterate over observations in this observation set
        """
        return ObservationSetIterator(self)



class RawAnalyzer:
    def run(self, context):
        pass

class ObservationAnalyzer:
    def run(self, context):
        pass
