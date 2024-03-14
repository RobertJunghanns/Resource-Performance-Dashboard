import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import pm4py
import warnings
import numpy as np
import pandas as pd
from src.framework.measures.resource_behavior_indicators import rbi_activity_completions
from src.framework.measures.case_performance_measures import case_duration
from src.framework.sampling import case_level_sampling
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
        log_path_synth_short = 'tests/data/synthetic_log_short.xes'  
        cls.event_log_synth_short = pm4py.read_xes(log_path_synth_short)
        log_path_synth_long = 'tests/data/synthetic_log_long.xes'  
        cls.event_log_synth_long = pm4py.read_xes(log_path_synth_long)
        log_path_synth_extra_long = 'tests/data/synthetic_log_extra_long.xes'  
        cls.event_log_synth_extra_long = pm4py.read_xes(log_path_synth_extra_long)
        log_path_real = 'tests/data/real_log_short.xes'  
        cls.event_log_real = pm4py.read_xes(log_path_real)


    def test_events_in_time_frame(self):
        t_start = pd.Timestamp("2011-01-01T03:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-01T06:30:00.000+02:00")
        events_in_time_frame = case_level_sampling.get_events_in_time_frame(self.event_log_synth_short, t_start, t_end)

        self.assertEqual(len(events_in_time_frame), 2)

    def test_events_not_in_time_frame(self):
        t_start = pd.Timestamp("2011-01-01T03:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-01T06:30:00.000+02:00")
        events_in_time_frame = case_level_sampling.get_events_not_in_time_frame(self.event_log_synth_short, t_start, t_end)

        self.assertEqual(len(events_in_time_frame), 11)

    def test_caseids_in_time_frame(self):
        t_start = pd.Timestamp("2010-12-31T23:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-01T06:30:00.000+02:00")
        caseids = case_level_sampling.get_caseids_in_time_frame(self.event_log_synth_short, t_start, t_end)

        self.assertEqual(caseids, np.array(['001']))

    def test_participating_resources(self):
        trace = activity_duration_estimation.get_trace(self.event_log_synth_short, '001')
        trace_prepared = activity_duration_estimation.prepare_trace(trace)
        resources = case_level_sampling.get_participating_resources(trace_prepared)

        np.testing.assert_array_equal(np.sort(resources), np.array(['1', '2', '3']))
    
    def test_participating_share(self):
        trace = activity_duration_estimation.get_trace(self.event_log_synth_short, '001')
        trace_prepared = activity_duration_estimation.prepare_trace(trace)
        share_r1 = case_level_sampling.participation_share(trace_prepared, '1')
        share_r2 = case_level_sampling.participation_share(trace_prepared, '2')
        share_r3 = case_level_sampling.participation_share(trace_prepared, '3')

        self.assertEqual(share_r1, 0)
        self.assertEqual(share_r2, 3/4)
        self.assertEqual(share_r3, 1/4)

    def test_case_level_sampling(self):
        t_start = pd.Timestamp("2010-12-31T23:30:00.000+02:00")
        t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")
        regression_data_cs = case_level_sampling.sample_regression_data_case(self.event_log_synth_long, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.CASE, rbi_function=rbi_activity_completions, performance_function=case_duration)
        regression_data_is = case_level_sampling.sample_regression_data_case(self.event_log_synth_long, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.INDIVIDUAL, rbi_function=rbi_activity_completions, performance_function=case_duration, individual_scope=pd.Timedelta(days=1))
        regression_data_ts = case_level_sampling.sample_regression_data_case(self.event_log_synth_long, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.TOTAL, rbi_function=rbi_activity_completions, performance_function=case_duration)

        # for three sampled (IV/DV): weighted activity completions and case duration
        expected_regression_data_cs = (np.array([7/3, 4/3, 7/4]), np.array([420., 420., 240.]))
        expected_regression_data_is = (np.array([11/3, 5/2, 7/3]), np.array([420., 420., 240.]))
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
            case_level_sampling.sample_regression_data_case(self.event_log_synth_long, t_start, t_end, case_limit=100, seed=999, scope='invalidScope', rbi_function=rbi_activity_completions, performance_function=case_duration)

    def test_lookup_information(self):
        t_start = pd.Timestamp("2011-01-01T01:00:00.000+02:00")
        t_end = pd.Timestamp("2011-01-03T07:00:00.000+02:00")
        _, _, lookup_information = case_level_sampling.sample_regression_data_case(self.event_log_synth_extra_long, t_start, t_end, case_limit=100, seed=999, scope=case_level_sampling.ScopeCase.CASE, rbi_function=rbi_activity_completions, performance_function=case_duration)

        case_id_info = lookup_information.get('case_id')
        trace_info = lookup_information.get('trace')
        resource_info = lookup_information.get('resources')

        expected_case_ids = ['001', '002']
        expected_traces = ['A->B->B->...2 activities...->F->G->H', 'A->A->B->B->C->D']
        expected_resources = ['1,2,3', '1,2,3']

        self.assertEqual(case_id_info[0], expected_case_ids[0])
        self.assertEqual(trace_info[0], expected_traces[0])
        self.assertEqual(resource_info[0], expected_resources[0])

        self.assertEqual(case_id_info[1], expected_case_ids[1])
        self.assertEqual(trace_info[1], expected_traces[1])
        self.assertEqual(resource_info[1], expected_resources[1])

if __name__ == '__main__':
    unittest.main()