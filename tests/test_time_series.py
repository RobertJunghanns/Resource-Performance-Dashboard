import unittest
import sys
import os
import pm4py
from datetime import datetime
from src.framework.sampling import time_series_sampling 
import warnings



class TestTimeSeriesFunctions(unittest.TestCase):

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

    def test_day_intervals(self):
        start_date = datetime(2022, 1, 2)
        end_date = datetime(2022, 1, 4)
        intervals = time_series_sampling.generate_time_period_intervals(start_date, end_date, 'day')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2022, 1, 2), datetime(2022, 1, 3)))
        self.assertEqual(intervals[1], (datetime(2022, 1, 3), datetime(2022, 1, 4)))

    def test_week_intervals(self):
        start_date = datetime(2022, 1, 1, 12, 0)
        end_date = datetime(2022, 1, 17, 12, 0)
        intervals = time_series_sampling.generate_time_period_intervals(start_date, end_date, 'week')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2022, 1, 3), datetime(2022, 1, 10)))
        self.assertEqual(intervals[1], (datetime(2022, 1, 10), datetime(2022, 1, 17)))

    def test_month_intervals(self):
        start_date = datetime(2022, 1, 29, 12, 0)
        end_date = datetime(2022, 4, 17, 12, 0)
        intervals = time_series_sampling.generate_time_period_intervals(start_date, end_date, 'month')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2022, 2, 1), datetime(2022, 3, 1)))
        self.assertEqual(intervals[1], (datetime(2022, 3, 1), datetime(2022, 4, 1)))

    def test_year_intervals(self):
        start_date = datetime(2019, 1, 1, 12, 0)
        end_date = datetime(2022, 1, 17, 12, 0)
        intervals = time_series_sampling.generate_time_period_intervals(start_date, end_date, 'year')
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0], (datetime(2020, 1, 1), datetime(2021, 1, 1)))
        self.assertEqual(intervals[1], (datetime(2021, 1, 1), datetime(2022, 1, 1)))

    def test_year_intervals_error(self):
        start_date = datetime(2019, 1, 1, 12, 0)
        end_date = datetime(2022, 1, 17, 12, 0)

        with self.assertRaises(ValueError):
            time_series_sampling.generate_time_period_intervals(start_date, end_date, 'no_time_period')
        
        self.assertTrue("Invalid period. Choose from 'day', 'week', 'month', 'year'.")

    def test_year_intervals_total(self):
        start_date = datetime(2019, 1, 1, 12, 0)
        end_date = datetime(2021, 1, 17, 12, 0)
        intervals = time_series_sampling.generate_until_end_period_intervals(start_date, end_date, 'year')
        self.assertEqual(len(intervals), 3)
        self.assertEqual(intervals[0], (datetime(2019, 1, 1, 12, 0), datetime(2020, 1, 1), datetime(2019, 1, 1, 12, 0)))
        self.assertEqual(intervals[1], (datetime(2019, 1, 1, 12, 0), datetime(2021, 1, 1), datetime(2020, 1, 1)))
        self.assertEqual(intervals[2], (datetime(2019, 1, 1, 12, 0), datetime(2021, 1, 17, 12, 0), datetime(2021, 1, 1)))

    def test_align_date_period(self):
        date = datetime(2019, 1, 1, 12, 0)
        result = time_series_sampling.align_date_to_period(date, 'day')
        self.assertEqual(result, datetime(2019, 1, 1))

    def test_day_period_name(self):
        date = datetime(2022, 1, 15)
        result = time_series_sampling.get_period_name(date, 'day')
        self.assertEqual(result, "Jan. 15, 2022")

    def test_week_period_name(self):
        date = datetime(2022, 1, 3) 
        result = time_series_sampling.get_period_name(date, 'week')
        self.assertEqual(result, "Week 1, 2022")

    def test_month_period_name(self):
        date = datetime(2022, 1, 15)
        result = time_series_sampling.get_period_name(date, 'month')
        self.assertEqual(result, "Jan. 2022")

    def test_year_period_name(self):
        date = datetime(2022, 1, 15)
        result = time_series_sampling.get_period_name(date, 'year')
        self.assertEqual(result, "2022")

    def test_invalid_period_name(self):
        date = datetime(2022, 1, 15)
        with self.assertRaises(ValueError):
            time_series_sampling.get_period_name(date, 'invalid')
        self.assertTrue("Invalid period. Choose from 'day', 'week', 'month', 'year'.")
        

if __name__ == '__main__':
    unittest.main()