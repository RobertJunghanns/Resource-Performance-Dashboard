import unittest
import pm4py
import pandas as pd
import pandas.testing as pdt
from src.model.utility import pickle_utility 
import warnings



class TestPickleUtilityFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        log_path = 'tests/data/test.xes'  
        cls.event_log = pm4py.read_xes(log_path)

    def test_pickle(self):
        pickle_utility.save_as_pickle(self.event_log, 'test')
        loaded_event_log = pickle_utility.load_from_pickle('test')

        pdt.assert_frame_equal(self.event_log, loaded_event_log)

    def test_pickle_no_filename(self):
        loaded_event_log = pickle_utility.load_from_pickle(None)

        pdt.assert_frame_equal(pd.DataFrame({}) , loaded_event_log)
    
    
if __name__ == '__main__':
    unittest.main()