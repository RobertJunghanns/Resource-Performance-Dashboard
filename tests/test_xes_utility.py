import unittest
import pm4py
import pandas as pd
from datetime import datetime
from src.framework.utility import xes_utility 
import warnings



class TestXESUtilityFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        self.assertEqual(completed_events_count, 44)

    def test_completed_events_error(self):
        with self.assertRaises(ValueError) as context:
            xes_utility.count_completed_events(self.event_log, lifecycle_column='non_existent_column')
        
        self.assertTrue("Column 'non_existent_column' not found in DataFrame" in str(context.exception))

    def test_day_intervals(self):
        start_date = datetime(2022, 1, 2)
        end_date = datetime(2022, 1, 4)
        intervals = xes_utility.generate_time_period_intervals(start_date, end_date, 'day')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2022, 1, 2), datetime(2022, 1, 3)))
        self.assertEqual(intervals[1], (datetime(2022, 1, 3), datetime(2022, 1, 4)))

    def test_week_intervals(self):
        start_date = datetime(2022, 1, 1, 12, 0)
        end_date = datetime(2022, 1, 17, 12, 0)
        intervals = xes_utility.generate_time_period_intervals(start_date, end_date, 'week')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2022, 1, 3), datetime(2022, 1, 10)))
        self.assertEqual(intervals[1], (datetime(2022, 1, 10), datetime(2022, 1, 17)))

    def test_month_intervals(self):
        start_date = datetime(2022, 1, 29, 12, 0)
        end_date = datetime(2022, 4, 17, 12, 0)
        intervals = xes_utility.generate_time_period_intervals(start_date, end_date, 'month')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2022, 2, 1), datetime(2022, 3, 1)))
        self.assertEqual(intervals[1], (datetime(2022, 3, 1), datetime(2022, 4, 1)))

    def test_year_intervals(self):
        start_date = datetime(2019, 1, 1, 12, 0)
        end_date = datetime(2022, 1, 17, 12, 0)
        intervals = xes_utility.generate_time_period_intervals(start_date, end_date, 'year')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2020, 1, 1), datetime(2021, 1, 1)))
        self.assertEqual(intervals[1], (datetime(2021, 1, 1), datetime(2022, 1, 1)))

    def test_year_intervals_error(self):
        start_date = datetime(2019, 1, 1, 12, 0)
        end_date = datetime(2022, 1, 17, 12, 0)

        with self.assertRaises(ValueError):
            xes_utility.generate_time_period_intervals(start_date, end_date, 'no_time_period')
        
        self.assertTrue("Invalid period. Choose from 'day', 'week', 'month', 'year'.")

    def test_year_intervals_total(self):
        start_date = datetime(2019, 1, 1, 12, 0)
        end_date = datetime(2021, 1, 17, 12, 0)
        intervals = xes_utility.generate_until_end_period_intervals(start_date, end_date, 'year')
        self.assertEqual(len(intervals), 3)
        self.assertEqual(intervals[0], (datetime(2019, 1, 1, 12, 0), datetime(2020, 1, 1), datetime(2019, 1, 1, 12, 0)))
        self.assertEqual(intervals[1], (datetime(2019, 1, 1, 12, 0), datetime(2021, 1, 1), datetime(2020, 1, 1)))
        self.assertEqual(intervals[2], (datetime(2019, 1, 1, 12, 0), datetime(2021, 1, 17, 12, 0), datetime(2021, 1, 1)))

    def test_align_date_period(self):
        date = datetime(2019, 1, 1, 12, 0)
        result = xes_utility.align_date_to_period(date, 'day')
        self.assertEqual(result, datetime(2019, 1, 1))

    def test_day_period_name(self):
        date = datetime(2022, 1, 15)
        result = xes_utility.get_period_name(date, 'day')
        self.assertEqual(result, "Jan. 15, 2022")

    def test_week_period_name(self):
        date = datetime(2022, 1, 3) 
        result = xes_utility.get_period_name(date, 'week')
        self.assertEqual(result, "Week 1, 2022")

    def test_month_period_name(self):
        date = datetime(2022, 1, 15)
        result = xes_utility.get_period_name(date, 'month')
        self.assertEqual(result, "Jan. 2022")

    def test_year_period_name(self):
        date = datetime(2022, 1, 15)
        result = xes_utility.get_period_name(date, 'year')
        self.assertEqual(result, "2022")

    def test_invalid_period_name(self):
        date = datetime(2022, 1, 15)
        with self.assertRaises(ValueError):
            xes_utility.get_period_name(date, 'invalid')
        self.assertTrue("Invalid period. Choose from 'day', 'week', 'month', 'year'.")
        

if __name__ == '__main__':
    unittest.main()