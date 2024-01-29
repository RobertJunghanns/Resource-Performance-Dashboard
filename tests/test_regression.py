import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import pm4py
import warnings
import numpy as np
import pandas as pd

from src.framework.measures.resource_behavior_indicators import rbi_distinct_activities
from src.framework.measures.case_performance_measures import case_duration
from src.framework.sampling import case_level_sampling
from src.framework import regression_analysis


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


    def test_rbi_sql(self): 
        t_start = pd.Timestamp("2010-12-31T23:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")
        regression_data_cs = case_level_sampling.sample_regression_data_case(self.event_log_simple_mt, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.CASE, rbi_function=rbi_distinct_activities, performance_function=case_duration)

        intercept, slope, r_squared, rpi_p_value, rpi_t_stat  = regression_analysis.fit_regression(regression_data_cs[0], regression_data_cs[1])

        expected_values = {
            "intercept": 324.22,
            "slope": 19.82, 
            "r_squared": 0.009, 
            "rpi_p_value": 0.939, 
            "rpi_t_stat": 0.096   
        }

        tolerance = 1e-2 
        self.assertAlmostEqual(intercept, expected_values['intercept'], delta=tolerance)
        self.assertAlmostEqual(slope, expected_values['slope'], delta=tolerance)
        self.assertAlmostEqual(r_squared, expected_values['r_squared'], delta=tolerance)
        self.assertAlmostEqual(rpi_p_value, expected_values['rpi_p_value'], delta=tolerance)
        self.assertAlmostEqual(rpi_t_stat, expected_values['rpi_t_stat'], delta=tolerance)

if __name__ == '__main__':
    unittest.main()