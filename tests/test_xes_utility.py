import unittest
import pm4py
import pandas as pd
from src.model.xes_utility import get_earliest_timestamp, get_latest_timestamp
import warnings


class TestXESUtilityFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        log_path = 'tests/data/BPIC15_1.xes'  
        cls.event_log = pm4py.read_xes(log_path)

    def test_earliest_timestamp(self):

        earliest = get_earliest_timestamp(self.event_log)
        expected_timestamp = pd.Timestamp('2010-10-04 22:00:00+00:00') 

        self.assertEqual(earliest, expected_timestamp)
    
    def test_latest_timestamp(self):

        latest = get_latest_timestamp(self.event_log)
        print(latest)
        expected_timestamp = pd.Timestamp('2015-07-31 22:00:00+0000') 

        self.assertEqual(latest, expected_timestamp)

if __name__ == '__main__':
    unittest.main()