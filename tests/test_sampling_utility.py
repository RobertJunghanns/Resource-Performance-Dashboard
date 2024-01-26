import unittest
import pm4py
import pandas as pd
from datetime import datetime
from src.model.utility import xes_utility 
import warnings



class TestSamplingUtilityFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        log_path = 'tests/data/test.xes'  
        cls.event_log = pm4py.read_xes(log_path)

        

if __name__ == '__main__':
    unittest.main()