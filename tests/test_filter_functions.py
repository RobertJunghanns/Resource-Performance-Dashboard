import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import pm4py
import warnings
from src.framework.utility import filter_functions 



class TestXESUtilityFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        log_path = 'tests/data/real_log_long.xes'  
        cls.event_log = pm4py.read_xes(log_path)

    def test_filter_direct_decline_bpic_12(self):
        original_case_ids = set(self.event_log['case:concept:name'].unique())
        filtered_event_logs = filter_functions.filter_direct_decline_bpic_12(self.event_log)
        filtered_case_ids = set(filtered_event_logs['case:concept:name'].unique())

        self.assertEqual(len(original_case_ids) - 1, len(filtered_case_ids))

    def test_filter_cancel_decline_bpic_12(self):
        original_case_ids = set(self.event_log['case:concept:name'].unique())
        filtered_event_logs = filter_functions.filter_cancel_decline_bpic_12(self.event_log)
        filtered_case_ids = set(filtered_event_logs['case:concept:name'].unique())

        self.assertEqual(len(original_case_ids) - 2, len(filtered_case_ids))

if __name__ == '__main__':
    unittest.main()