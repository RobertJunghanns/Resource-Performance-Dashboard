import unittest
import pm4py
import pandas as pd
from src.model.xes_utility import get_earliest_timestamp, get_latest_timestamp, get_unique_resources, df_to_json, json_to_df
import warnings


class TestXESUtilityFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        log_path = 'tests/data/BPIC15_1.xes'  
        cls.event_log = json_to_df(df_to_json(pm4py.read_xes(log_path))) #simulate the (de-)serialization for storing the df in dcc.Store
        print(cls.event_log)

    def test_earliest_timestamp(self):
        earliest = get_earliest_timestamp(self.event_log)
        expected_timestamp = pd.Timestamp('2010-10-04 22:00:00+00:00')

        self.assertEqual(earliest, expected_timestamp)
    
    def test_latest_timestamp(self):
        latest = get_latest_timestamp(self.event_log)
        expected_timestamp = pd.Timestamp('2015-07-31 22:00:00+0000') 

        self.assertEqual(latest, expected_timestamp)
    
    def test_unique_resources(self):
        unique_resources = get_unique_resources(self.event_log)
        expected_resources = {'6', '11345232', '560999', '1898401', '12941730', '10716070', '9264148', '560894', '560881', '5726485', '560872', '2670601', '560464', '4936828', '560890', '560925', '560950', '3273854', '560589', '3175153', '11744364', '560462', '560912'}

        self.assertEqual(unique_resources, expected_resources)

if __name__ == '__main__':
    unittest.main()