import unittest
import sys
import os
import pm4py
import warnings
import pandas as pd
import pandas.testing as pdt
from src.framework.utility import sampling_utility
from src.framework.utility import xes_utility




class TestSamplingUtilityFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Add the src directory to the sys.path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        log_path = 'tests/data/test.xes'  
        cls.event_log = pm4py.read_xes(log_path)
        event_log_simple_path = 'tests/data/test_simple.xes'  
        cls.event_log_simple = pm4py.read_xes(event_log_simple_path)
        cls.case_ids = ['case1', 'case2', 'case3', 'case4', 'case5']

    def test_get_n_case_ids_less(self):
        
        sampled_ids = sampling_utility.get_n_case_ids(self.case_ids, 3)
        self.assertEqual(len(sampled_ids), 3)

    def test_get_n_case_ids_more(self):
        sampled_ids = sampling_utility.get_n_case_ids(self.case_ids, len(self.case_ids))
        self.assertEqual(len(sampled_ids), len(self.case_ids))

    def test_get_n_events_less(self):
        sampled_events = sampling_utility.get_n_events(self.event_log, 5)
        self.assertEqual(len(sampled_events), 5)

    def test_get_n_events_more(self):
        sampled_events = sampling_utility.get_n_events(self.event_log, len(self.event_log))
        self.assertEqual(len(sampled_events), len(self.event_log))

    def test_get_trace(self):
        sampled_trace = sampling_utility.get_trace(self.event_log, '173691')
        expected_trace = self.event_log.loc[self.event_log['case:concept:name'] == '173691']

        pdt.assert_frame_equal(sampled_trace, expected_trace)

    def test_group_equal_timestamp_events(self):
        trace = sampling_utility.get_trace(self.event_log, '173691')
        grouped_trace = sampling_utility.group_equal_timestamp_events(trace)

        grouped_event_1 = grouped_trace[grouped_trace['concept:name'] == 'A_FINALIZED + O_SELECTED'] # same timestamps & resource
        grouped_event_2 = grouped_trace[grouped_trace['concept:name'] == 'O_SELECTED + O_CANCELLED'] # same timestamps & resource
        grouped_event_3 = grouped_trace[grouped_trace['concept:name'] == 'A_APPROVED + A_REGISTERED + A_ACTIVATED'] # same timestamps & resource
        grouped_event_4 = grouped_trace[grouped_trace['concept:name'] == 'W_Valideren aanvraag + W_Valideren aanvraag'] # same timestamps & resource but have a start event

        self.assertEqual(len(grouped_event_1), 1)
        self.assertEqual(len(grouped_event_2), 1)
        self.assertEqual(len(grouped_event_3), 1)
        self.assertEqual(len(grouped_event_4), 0)
        
    def test_add_activity_duration(self):
        trace = sampling_utility.get_trace(self.event_log_simple, '001')
        trace_activity_duration = sampling_utility.add_activity_durations_to_trace(trace)
        durations = trace_activity_duration['duration']

        expected_durations = pd.Series(
            [pd.Timedelta(0), pd.Timedelta(0), pd.Timedelta(hours=1), pd.Timedelta(hours=2), pd.Timedelta(hours=1)],
            name='duration'
        )

        pdt.assert_series_equal(durations, expected_durations)

    def test_prepare_trace(self):
        trace = sampling_utility.get_trace(self.event_log_simple, '001')
        trace_prepared = sampling_utility.prepare_trace(trace)

        self.assertEqual(len(xes_utility.get_column_names(trace)) + 1, len(xes_utility.get_column_names(trace_prepared)))
        self.assertLessEqual(len(trace_prepared), len(trace))

if __name__ == '__main__':
    unittest.main()