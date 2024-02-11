import pandas as pd

from datetime import timedelta

def align_date_to_period(date, period, next_period=False):
    period_logic = {
        'day': {'align': lambda d: d.replace(hour=0, minute=0, second=0, microsecond=0),
                'shift': lambda d: d + timedelta(days=1)},
        'week': {'align': lambda d: (d - timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
                 'shift': lambda d: d + timedelta(weeks=1)},
        'month': {'align': lambda d: d.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                  'shift': lambda d: d + pd.DateOffset(months=1)},
        'year': {'align': lambda d: d.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
                 'shift': lambda d: d + pd.DateOffset(years=1)}
    }

    if period not in period_logic:
        raise ValueError("Invalid period. Choose from 'day', 'week', 'month', 'year'.")

    aligned_date = period_logic[period]['align'](date)

    if next_period:
        aligned_date = period_logic[period]['shift'](aligned_date)

    return aligned_date

def generate_time_period_intervals(timestamp_from, timestamp_to, period):
    intervals = []
    current_start = timestamp_from

    while current_start < timestamp_to:
        current_end = align_date_to_period(current_start, period, next_period=True)

        if current_end > timestamp_to:
            current_end = timestamp_to

        intervals.append((current_start, current_end))
        current_start = current_end

    # Remove the first interval if it's shorter than the others
    if len(intervals) > 1 and (intervals[0][1] - intervals[0][0]) != (intervals[1][1] - intervals[1][0]):
        intervals.pop(0)

    # Remove the last interval if it's shorter than the others
    if len(intervals) > 1 and (intervals[-1][1] - intervals[-1][0]) != (intervals[-2][1] - intervals[-2][0]):
        intervals.pop()

    return intervals

def generate_until_end_period_intervals(timestamp_from, timestamp_to, period):
    intervals = []
    current_start = timestamp_from

    while current_start < timestamp_to:
        current_end = align_date_to_period(current_start, period, next_period=True)

        if current_end > timestamp_to:
            current_end = timestamp_to

        intervals.append((timestamp_from, current_end, current_start)) #allways start from start_date
        current_start = current_end

    return intervals

def get_period_name(date, period):
    if period == 'day':
        return date.strftime("%b. %d, %Y")
    elif period == 'week':
        week_num = date.isocalendar()[1]
        year = date.isocalendar()[0]
        return f"Week {week_num}, {year}"
    elif period == 'month':
        return date.strftime("%b. %Y")
    elif period == 'year':
        return date.strftime("%Y")
    else:
        raise ValueError("Invalid period. Choose from 'day', 'week', 'month', 'year'.")