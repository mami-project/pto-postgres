#
# Path Transparency Observatory
# Analysis Runtime
#

class AnalysisContext:

    def __init__(self, ):
        pass
        
    def create_observation_set(self, ):
        pass

class ObservationSetWriter:

    def observe(self, start, end, path, condition, value):
        pass

    def complete(self):
        """
        Finish writing observations to this observation set
        """
        pass

class ObservationSetReader:

    def __iter__(self):
        """
        Iterate over observations in this observation set
        """
        return self

    def __next__(self):
        """
        Get the next observation in the observation set, when used as an iterator
        """
        pass

class RawAnalyzer:
    def run(self, context, some_handle_to_spark):
        pass

class ObservationAnalyzer:
    def run(self, context, reader):
        pass