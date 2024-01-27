import unittest
import sys
import os
import pm4py
import pandas as pd
from datetime import datetime
from src.framework.utility import xes_utility 
import warnings



class TestXESUtilityFunctions(unittest.TestCase):

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

    def test_earliest_timestamp(self):
        earliest = xes_utility.get_earliest_timestamp(self.event_log)
        expected_timestamp = pd.Timestamp('2011-10-01 00:38:44.546000+0200')

        self.assertEqual(earliest, expected_timestamp)
    
    def test_latest_timestamp(self):
        latest = xes_utility.get_latest_timestamp(self.event_log)
        expected_timestamp = pd.Timestamp('2011-10-13 10:37:37.026000+0200') 

        self.assertEqual(latest, expected_timestamp)
    
    def test_unique_resources(self):
        unique_resources = xes_utility.get_unique_resources(self.event_log)
        expected_resources = {'112', '10913', '10629', '11049', '10862', '10809', '11120'}

        self.assertEqual(unique_resources, expected_resources)

    def test_column_names(self):
        column_names = xes_utility.get_column_names(self.event_log)
        expected_columns = ['org:resource', 'lifecycle:transition', 'concept:name', 'time:timestamp', 'case:REG_DATE', 'case:concept:name', 'case:AMOUNT_REQ']

        self.assertEqual(column_names, expected_columns)

    def test_unique_cases(self):
        unique_cases_count = xes_utility.count_unique_cases(self.event_log)

        self.assertEqual(unique_cases_count, 2)

    def test_unique_cases_error(self):
        with self.assertRaises(ValueError) as context:
            xes_utility.count_unique_cases(self.event_log, case_id_column='non_existent_column')
        
        self.assertTrue("Column 'non_existent_column' not found in DataFrame" in str(context.exception))

    def test_completed_events(self):
        completed_events_count = xes_utility.count_completed_events(self.event_log)
        self.assertEqual(completed_events_count, 46)

    def test_completed_events_error(self):
        with self.assertRaises(ValueError) as context:
            xes_utility.count_completed_events(self.event_log, lifecycle_column='non_existent_column')
        
        self.assertTrue("Column 'non_existent_column' not found in DataFrame" in str(context.exception))     

if __name__ == '__main__':
    unittest.main()