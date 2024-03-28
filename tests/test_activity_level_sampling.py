import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import pm4py
import warnings
import numpy as np
import pandas as pd
from src.framework.measures.resource_behavior_indicators import rbi_activity_completions
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
        log_path_synth_short = 'tests/data/synthetic_log_short.xes'  
        cls.event_log_synth_short = pm4py.read_xes(log_path_synth_short)
        log_path_synth_long = 'tests/data/synthetic_log_long.xes'  
        cls.event_log_synth_long = pm4py.read_xes(log_path_synth_long)
        log_path_synth_extra_long = 'tests/data/synthetic_log_extra_long.xes'  
        cls.event_log_synth_extra_long = pm4py.read_xes(log_path_synth_extra_long)

    def test_filter_event_log(self):
        t_start = pd.Timestamp("2011-01-02T08:00:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")

        complete_events_included_1 = activity_level_sampling.filter_event_log(self.event_log_synth_long, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1')
        complete_events_included_2 = activity_level_sampling.filter_event_log(self.event_log_synth_long, t_start, t_end)

        self.assertEqual(len(complete_events_included_1), 4)
        self.assertEqual(len(complete_events_included_2), 5)

    def test_activity_level_sampling_progress_print(self):
        t_start = pd.Timestamp("2010-01-01T01:00:00.000+02:00")
        t_end = pd.Timestamp("2012-01-03T07:00:00.000+02:00")
        rbi_values, _, _ = activity_level_sampling.sample_regression_data_activity(self.event_log_synth_extra_long, t_start, t_end, filter_event_attribute='case:concept:name', filter_event_value='017', activity_limit=15, seed=999, scope=activity_level_sampling.ScopeActivity.ACTIVITY, rbi_function=rbi_activity_completions, performance_function=activity_duration)

        self.assertEqual(len(rbi_values), 11)

    def test_activity_level_sampling(self):
        t_start = pd.Timestamp("2011-01-02T08:00:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")


        regression_data_cs = activity_level_sampling.sample_regression_data_activity(self.event_log_synth_long, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope=activity_level_sampling.ScopeActivity.ACTIVITY, rbi_function=rbi_activity_completions, performance_function=activity_duration)

        regression_data_is = activity_level_sampling.sample_regression_data_activity(self.event_log_synth_long, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope=activity_level_sampling.ScopeActivity.INDIVIDUAL, rbi_function=rbi_activity_completions, performance_function=activity_duration, individual_scope = pd.Timedelta(days=1))

        regression_data_ts = activity_level_sampling.sample_regression_data_activity(self.event_log_synth_long, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope=activity_level_sampling.ScopeActivity.TOTAL, rbi_function=rbi_activity_completions, performance_function=activity_duration)

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
            activity_level_sampling.sample_regression_data_activity(self.event_log_synth_long, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='1', activity_limit=10, seed=999, scope='invalid scope', rbi_function=rbi_activity_completions, performance_function=activity_duration)

    def test_lookup_information(self):
        t_start = pd.Timestamp("2011-01-01T01:00:00.000+02:00")
        t_end = pd.Timestamp("2011-01-03T07:00:00.000+02:00")
        _, _, lookup_information = activity_level_sampling.sample_regression_data_activity(self.event_log_synth_extra_long, t_start, t_end, filter_event_attribute='org:resource', filter_event_value='5', activity_limit=10, seed=999, scope=activity_level_sampling.ScopeActivity.ACTIVITY, rbi_function=rbi_activity_completions, performance_function=activity_duration)

        case_id_info = lookup_information.get('case_id')
        trace_info = lookup_information.get('activity_id')
        resource_info = lookup_information.get('resource')

        expected_case_ids = ['018', '018']
        expected_activity_ids = ['C', 'D']
        expected_resources = ['5', '5']

        self.assertEqual(case_id_info[0], expected_case_ids[0])
        self.assertEqual(trace_info[0], expected_activity_ids[0])
        self.assertEqual(resource_info[0], expected_resources[0])

        self.assertEqual(case_id_info[1], expected_case_ids[1])
        self.assertEqual(trace_info[1], expected_activity_ids[1])
        self.assertEqual(resource_info[1], expected_resources[1])

if __name__ == '__main__':
    unittest.main()