import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import pm4py
import warnings
import numpy as np
import pandas as pd
from src.framework.measures import case_performance_measures
from src.framework.sampling import activity_duration_estimation


def sort_tuple_data(data_tuple):
    return (np.sort(data_tuple[0]), np.sort(data_tuple[1]))

class TestCaseLevelSampling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        event_log_simple_mt_path = 'tests/data/test_simple_more_traces.xes'  
        cls.event_log_simple_mt = pm4py.read_xes(event_log_simple_mt_path)


    def test_case_duration_and_sql(self):
        sampled_trace = activity_duration_estimation.get_trace(self.event_log_simple_mt, '001')

        case_duration_sql = """
        SELECT
            (CAST(strftime('%s', MAX([time:timestamp])) AS FLOAT) - 
            CAST(strftime('%s', MIN([time:timestamp])) AS FLOAT)) / 60
        FROM
            trace
        """    

        case_duration_sql = case_performance_measures.sql_to_case_performance_metric(sampled_trace, case_duration_sql)
        case_duration = case_performance_measures.case_duration(sampled_trace)

        self.assertEqual(case_duration_sql, case_duration)

    def test_sql_no_return(self):
        sampled_trace = activity_duration_estimation.get_trace(self.event_log_simple_mt, '001')

        case_duration_sql = """
        SELECT COUNT([org:resource]) FROM trace WHERE [org:resource] = 'invalid'
        """    

        invalud_performance = case_performance_measures.sql_to_case_performance_metric(sampled_trace, case_duration_sql)
        

        self.assertEqual(invalud_performance, 0)

if __name__ == '__main__':
    unittest.main()