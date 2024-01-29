import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import pm4py
import warnings
import numpy as np
import pandas as pd
from src.framework.measures.resource_behavior_indicators import rbi_distinct_activities
from src.framework.measures.activity_performance_measures import activity_duration
from src.framework.sampling import activity_level_sampling

def sort_tuple_data(data_tuple):
    return (np.sort(data_tuple[0]), np.sort(data_tuple[1]))

class TestCaseLevelSampling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        event_log_simple_path = 'tests/data/test_simple.xes'  
        cls.event_log_simple = pm4py.read_xes(event_log_simple_path)
        event_log_simple_mt_path = 'tests/data/test_simple_more_traces.xes'  
        cls.event_log_simple_mt = pm4py.read_xes(event_log_simple_mt_path)

    def test_get_included_events(self):
        t_start = pd.Timestamp("2011-01-02T08:00:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")

        complete_events_included_1 = activity_level_sampling.get_included_events(self.event_log_simple_mt, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1')
        complete_events_included_2 = activity_level_sampling.get_included_events(self.event_log_simple_mt, t_start, t_end)

        self.assertEqual(len(complete_events_included_1), 4)
        self.assertEqual(len(complete_events_included_2), 5)

    def test_activity_level_sampling(self):
        t_start = pd.Timestamp("2011-01-02T08:00:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")


        regression_data_cs = activity_level_sampling.sample_regression_data_activity(self.event_log_simple_mt, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope=activity_level_sampling.ScopeActivity.ACTIVITY, rbi_function=rbi_distinct_activities, performance_function=activity_duration)

        regression_data_is = activity_level_sampling.sample_regression_data_activity(self.event_log_simple_mt, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope=activity_level_sampling.ScopeActivity.INDIVIDUAL, rbi_function=rbi_distinct_activities, performance_function=activity_duration, individual_scope = pd.Timedelta(days=1))

        regression_data_ts = activity_level_sampling.sample_regression_data_activity(self.event_log_simple_mt, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope=activity_level_sampling.ScopeActivity.TOTAL, rbi_function=rbi_distinct_activities, performance_function=activity_duration)

        expected_regression_data_cs = (np.array([0., 1., 2., 0.]), np.array([  0.,  60., 120.,  60.]))
        expected_regression_data_is = (np.array([3., 4., 6., 6.]), np.array([  0.,  60., 120.,  60.]))
        expected_regression_data_ts = (np.array([5., 6., 8., 8.]), np.array([  0.,  60., 120.,  60.]))

        sorted_regression_data_cs = sort_tuple_data(regression_data_cs)
        sorted_expected_data_cs = sort_tuple_data(expected_regression_data_cs)

        sorted_regression_data_is = sort_tuple_data(regression_data_is)
        sorted_expected_data_is = sort_tuple_data(expected_regression_data_is)

        sorted_regression_data_ts = sort_tuple_data(regression_data_ts)
        sorted_expected_data_ts = sort_tuple_data(expected_regression_data_ts)

        np.testing.assert_allclose(sorted_regression_data_cs, sorted_expected_data_cs, rtol=1e-5)
        np.testing.assert_allclose(sorted_regression_data_is, sorted_expected_data_is, rtol=1e-5)
        np.testing.assert_allclose(sorted_regression_data_ts, sorted_expected_data_ts, rtol=1e-5)
        
    def test_activity_level_sampling_error(self):
        t_start = pd.Timestamp("2011-01-02T08:00:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")
        
        with self.assertRaises(ValueError):
            activity_level_sampling.sample_regression_data_activity(self.event_log_simple_mt, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope='invalid scope', rbi_function=rbi_distinct_activities, performance_function=activity_duration)

if __name__ == '__main__':
    unittest.main()