import unittest
import sys
import os
import pm4py
import warnings
import numpy as np
import pandas as pd
import pandas.testing as pdt
from src.framework.measures.resource_behavior_indicators import rbi_distinct_activities
from src.framework.measures.case_performance_measures import case_duration
from src.framework.sampling import case_level_sampling
from src.framework.utility import sampling_utility

def sort_tuple_data(data_tuple):
    return (np.sort(data_tuple[0]), np.sort(data_tuple[1]))

class TestCaseLevelSampling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Add the src directory to the sys.path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        event_log_simple_path = 'tests/data/test_simple.xes'  
        cls.event_log_simple = pm4py.read_xes(event_log_simple_path)
        event_log_simple_mt_path = 'tests/data/test_simple_more_traces.xes'  
        cls.event_log_simple_mt = pm4py.read_xes(event_log_simple_mt_path)


    def test_events_in_time_frame(self):
        t_start = pd.Timestamp("2011-01-01T03:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-01T06:30:00.000+02:00")
        events_in_time_frame = case_level_sampling.get_events_in_time_frame(self.event_log_simple, t_start, t_end)

        self.assertEqual(len(events_in_time_frame), 2)

    def test_events_not_in_time_frame(self):
        t_start = pd.Timestamp("2011-01-01T03:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-01T06:30:00.000+02:00")
        events_in_time_frame = case_level_sampling.get_events_not_in_time_frame(self.event_log_simple, t_start, t_end)

        self.assertEqual(len(events_in_time_frame), 3)

    def test_caseids_in_time_frame(self):
        t_start = pd.Timestamp("2010-12-31T23:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-01T06:30:00.000+02:00")
        caseids = case_level_sampling.get_caseids_in_time_frame(self.event_log_simple, t_start, t_end)

        self.assertEqual(caseids, np.array(['001']))

    def test_participating_resources(self):
        trace = sampling_utility.get_trace(self.event_log_simple, '001')
        trace_prepared = sampling_utility.prepare_trace(trace)
        resources = case_level_sampling.get_participating_resources(trace_prepared)

        np.testing.assert_array_equal(np.sort(resources), np.array(['1', '2', '3']))
    
    def test_participating_share(self):
        trace = sampling_utility.get_trace(self.event_log_simple, '001')
        trace_prepared = sampling_utility.prepare_trace(trace)
        share_r1 = case_level_sampling.participation_share(trace_prepared, '1')
        share_r2 = case_level_sampling.participation_share(trace_prepared, '2')
        share_r3 = case_level_sampling.participation_share(trace_prepared, '3')

        self.assertEqual(share_r1, 0)
        self.assertEqual(share_r2, 3/4)
        self.assertEqual(share_r3, 1/4)

    def test_case_level_sampling(self):
        t_start = pd.Timestamp("2010-12-31T23:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")
        regression_data_cs = case_level_sampling.sample_regression_data_case(self.event_log_simple_mt, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.CASE, rbi_function=rbi_distinct_activities, performance_function=case_duration)
        regression_data_is = case_level_sampling.sample_regression_data_case(self.event_log_simple_mt, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.INDIVIDUAL, rbi_function=rbi_distinct_activities, performance_function=case_duration, individual_scope=pd.Timedelta(days=1))
        regression_data_ts = case_level_sampling.sample_regression_data_case(self.event_log_simple_mt, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.TOTAL, rbi_function=rbi_distinct_activities, performance_function=case_duration)

        expected_regression_data_cs = (np.array([7/3, 4/3, 7/4]), np.array([420., 420., 240.]))
        expected_regression_data_is = (np.array([5, 7/2, 5/2]), np.array([420., 420., 240.]))
        expected_regression_data_ts = (np.array([7, 19/6, 7/4]), np.array([420., 420., 240.]))

        sorted_regression_data_cs = sort_tuple_data(regression_data_cs)
        sorted_expected_data_cs = sort_tuple_data(expected_regression_data_cs)

        sorted_regression_data_is = sort_tuple_data(regression_data_is)
        sorted_expected_data_is = sort_tuple_data(expected_regression_data_is)

        sorted_regression_data_ts = sort_tuple_data(regression_data_ts)
        sorted_expected_data_ts = sort_tuple_data(expected_regression_data_ts)

        np.testing.assert_allclose(sorted_regression_data_cs, sorted_expected_data_cs, rtol=1e-5)
        np.testing.assert_allclose(sorted_regression_data_is, sorted_expected_data_is, rtol=1e-5)
        np.testing.assert_allclose(sorted_regression_data_ts, sorted_expected_data_ts, rtol=1e-5)

    def test_case_level_sampling_error(self):
        t_start = pd.Timestamp("2010-12-31T23:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")
        
        with self.assertRaises(ValueError):
            case_level_sampling.sample_regression_data_case(self.event_log_simple_mt, t_start, t_end, case_limit=100, seed=999, scope='invalidScope', rbi_function=rbi_distinct_activities, performance_function=case_duration)

if __name__ == '__main__':
    unittest.main()