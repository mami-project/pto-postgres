#
# Path Transparency Observatory
# Analysis Runtime
#

from ptoweb import get_db

class AnalysisContext:

    def __init__(self):
        pass
        
    def create_observation_set(self, name):
        set = get_db().insert('observation_set', name=name)
        return ObservationSetWriter(set.id)

class ObservationSetWriter:
    
    def __init__(self, set_id):
        self.observation_set_id = set_id

    def observe(self, start_time, end_time, path, condition, value):
        if vaue is None:
            get_db().insert('observation', full_path=path, time_from=start_time, time_to=end_time, condition=condition, observation_set=self.observation_set_id)
        else:
            get_db().insert('observation', full_path=path, time_from=start, time_to=end, condition=condition, val_n=value, observation_set=self.observation_set_id)
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
