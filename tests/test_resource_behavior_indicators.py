import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import pm4py
import warnings
import numpy as np
import pandas as pd
from src.framework.measures import resource_behavior_indicators


def sort_tuple_data(data_tuple):
    return (np.sort(data_tuple[0]), np.sort(data_tuple[1]))

class TestCaseLevelSampling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress specific warnings from pm4py
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        #import xes file(s)
        event_log_simple_mt_path = 'tests/data/test_simple_more_traces.xes'  
        cls.event_log_simple_mt = pm4py.read_xes(event_log_simple_mt_path)
        cls.t_start = pd.Timestamp("2010-12-31T23:30:00.000+02:00")
        cls.t_end = pd.Timestamp("2011-01-07T06:30:00.000+02:00")
        cls.resource_id = '1'
        cls.concept_name = 'A'  # For tests that require a concept name
        cls.interaction_resource_id = 'B'  # For interaction tests


    def test_rbi_sql(self):        
        rbi_sql="""
        SELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)
        FROM (
            SELECT
                (SELECT COUNT([concept:name])
                FROM event_log
                WHERE [org:resource] = '{r}'
                AND [concept:name] = 'A') AS activity,
                (SELECT COUNT([concept:name])
                FROM event_log
                WHERE [org:resource] = '{r}') AS all_activities
        ) AS count"""

        result = resource_behavior_indicators.sql_to_rbi(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id, sql_query=rbi_sql)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
    
    def test_rbi_sql_no_return(self):
        
        rbi_sql="""
        SELECT COUNT([concept:name])
                FROM event_log
                WHERE [org:resource] = '{r}'
                AND [concept:name] = 'invalid'"""

        with self.assertRaises(ValueError) as context:
            resource_behavior_indicators.sql_to_rbi(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id, sql_query=rbi_sql)

        self.assertTrue("SQL query result is not numeric." in str(context.exception))
    
    def test_rbi_distinct_activities(self):
        result = resource_behavior_indicators.rbi_distinct_activities(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_activity_completions(self):
        result = resource_behavior_indicators.rbi_activity_completions(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_activity_frequency(self):
        result = resource_behavior_indicators.rbi_activity_fequency(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id, self.concept_name)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)
    
    def test_rbi_average_workload(self):
        result = resource_behavior_indicators.rbi_average_workload(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_multitasking(self):
        result = resource_behavior_indicators.rbi_multitasking(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_average_duration_activity(self):
        result = resource_behavior_indicators.rbi_average_duration_activity(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id, self.concept_name)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)
    
    def test_rbi_case_completions(self):
        result = resource_behavior_indicators.rbi_case_completions(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_average_duration_activity(self):
        result = resource_behavior_indicators.rbi_average_duration_activity(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id, self.concept_name)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_interaction_two_resources(self):
        result = resource_behavior_indicators.rbi_interaction_two_resources(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id, self.interaction_resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_social_position(self):
        result = resource_behavior_indicators.rbi_social_position(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

    def test_rbi_fraction_case_completions(self):
        result = resource_behavior_indicators.rbi_fraction_case_completions(self.event_log_simple_mt, self.t_start, self.t_end, self.resource_id)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0)

        

if __name__ == '__main__':
    unittest.main()