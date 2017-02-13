import json
import dateutil.parser

from arun import Observation

import pandas as pd

class PathspiderECNRawAnalyzer:
    """
    Convert NDJSON files from PathSpider's ECN plugin into 
    PTO observations.
    """
    def __init__(self):
        pass

    def run(self, reader, writer, metadata):

        writer.begin()
        
        writer['pathspider.ecn'] = 'yes'

        for line in reader:
            raw_obs = json.loads(line)

            for condition in raw_obs['conditions']:
                writer.observe(start_time = dateutil.parser.parse(raw_obs['time']['from']),
                               end_time = dateutil.parser.parse(raw_obs['time']['to']),
                               path = [raw_obs['sip'], '*', raw_obs['dip']],
                               condition = condition,
                               value = None)


        writer.commit()


    def interested(self, metadata):
        return metadata['format'] == 'ps-ecn-ndjson' || metadata['format'] == 'ps-ecn-ndjson-bz2'

def observations_to_dataframe(observations, conditions):
    # create a dataframe from an observation iterator, 
    # with a boolean column for each of the specified conditions
    pass

def condition_counts_by_target(df):
    # group observation dataframe by target, 
    # sum condition counts, min/max time interval
    pass

class PathspiderECNSuperAnalyzer:
    """
    Create superconditions as an intermediate step 
    toward analyzing path dependency of ECN connectivity
    """

    def __init__(self):
        pass

    def run(self, observations, writer):

        # Pull everything into a dataframe. (RAM is good. More RAM is better.)
        df = observations_to_dataframe(observations, ['ecn.connectivity.works',
                                                      'ecn.connectivity.broken',
                                                      'ecn.connectivity.transient',
                                                      'ecn.connectivity.offline'])

        # now mutate the DF to an indexed-by-destination count of conditions by condition,
        # expanding start_time and end_time to the full interval covered; output is sdf
        # FIXME not done yet
        sdf = condition_counts_by_target(df)

        # calculate intermediate conditions
        sdf['int_e1seen'] = (sdf['ecn.connectivity.works'] + sdf['ecn.connectivity.transient']) > 0
        sdf['int_e0seen'] = (sdf['ecn.connectivity.works'] + sdf['ecn.connectivity.broken']) > 0

        # calculate super conditions
        sdf['super_works'] =         sdf['int_e0seen'] & sdf['int_e1seen']
        sdf['super_offline'] =      ~sdf['int_e0seen'] & ~sdf['int_e1seen']
        sdf['super_broken'] = (     (sdf['ecn.connectivity.broken'] > 0) & 
                                    (sdf['ecn.connectivity.works'] == 0) & 
                                    (sdf['ecn.connectivity.transient'] == 0)) 
        sdf['super_transient'] = (  (sdf['ecn.connectivity.transient'] > 0) & 
                                    (sdf['ecn.connectivity.works'] == 0) & 
                                    (sdf['ecn.connectivity.broken'] == 0)) 

        writer.begin()
        writer['pathspider.ecn.super'] = "yes"

        # and iterate

        for target in sdf.loc[:,['start_time','end_time',
                                 'super_works','super_offline',
                                 'super_broken','super_transient','super_weird']].itertuples():

            if target.super_works:
                condition = "ecn.connectivity.super.works"
            elif target.super_broken:
                condition = "ecn.connectivity.super.broken"
            elif target.super_transient:
                condition = "ecn.connectivity.super.transient"
            elif target.super_offline:
                condition = "ecn.connectivity.super.offline"
            elif target.super_offline:
                condition = "ecn.connectivity.super.weird"

            writer.observe(start_time = target.start_time,
                           end_time =  target.end_time,
                           path = ['*', target.Index],
                           condition = condition,
                           value = None)

        writer.commit()

    def interested(self, conditions, metadata):
        if     'ecn.connectivity.works' not in conditions && \
               'ecn.connectivity.broken' not in conditions && \
               'ecn.connectivity.transient' not in conditions && \
               'ecn.connectivity.offline' not in conditions:
            return false

        return 'pathspider.ecn' in metadata


class PathspiderECNPathDepAnalyzer:
    def run(self, observations, writer):
        # Pull everything into a dataframe. (RAM is good. More RAM is better.)
        df = observations_to_dataframe(observations, ['ecn.connectivity.super.works',
                                                      'ecn.connectivity.super.broken',
                                                      'ecn.connectivity.super.transient',
                                                      'ecn.connectivity.super.offline',
                                                      'ecn.connectivity.super.weird'])

        sdf = condition_counts_by_target(df)

        sdf['path_dep'] = ( (sdf['ecn.connectivity.super.broken'] >= 1) &
                            (sdf['ecn.connectivity.super.works'] >= 1) &
                            (sdf['ecn.connectivity.super.offline'] == 0) &
                            (sdf['ecn.connectivity.super.transient'] == 0) &
                            (sdf['ecn.connectivity.super.weird'] == 0))

        sdf['site_dep'] = ( (sdf['ecn.connectivity.super.broken'] >= 1) &
                            (sdf['ecn.connectivity.super.works'] == 0) &
                            (sdf['ecn.connectivity.super.offline'] == 0) &
                            (sdf['ecn.connectivity.super.transient'] == 0) &
                            (sdf['ecn.connectivity.super.weird'] == 0))

        writer.begin()
        writer['pathspider.ecn.dependency'] = 'yes'

        for target in sdf.loc[:,['start_time','end_time',
                                 'path_dep', 'site_dep']].itertuples():

            if target.path_dep:
                condition = "ecn.connectivity.path_dependent"
            elif target.site_dep:
                condition = "ecn.connectivity.site_dependent"
            else
                condition = None

            if condition is not None:
                writer.observe(start_time = target.start_time,
                               end_time =  target.end_time,
                               path = ['*', target.Index],
                               condition = condition,
                               value = None)

    def interested(self, conditions, metadata):
        if     'ecn.connectivity.super.works' not in conditions && \
               'ecn.connectivity.super.broken' not in conditions && \
               'ecn.connectivity.super.transient' not in conditions && \
               'ecn.connectivity.super.offline' not in conditions && \
               'ecn.connectivity.super.weird' not in conditions
            return false

        return 'pathspider.ecn.super' in metadata
 