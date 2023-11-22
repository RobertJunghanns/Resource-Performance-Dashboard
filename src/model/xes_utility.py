import pandas as pd
from io import StringIO
from datetime import datetime as dt
from datetime import timedelta

def get_earliest_timestamp(event_log: pd.DataFrame) -> pd.Timestamp:
    earliest_timestamp = event_log['time:timestamp'].min()
    return earliest_timestamp

def get_latest_timestamp(event_log: pd.DataFrame) -> pd.Timestamp:
    latest_timestamp = event_log['time:timestamp'].max()
    return latest_timestamp

def get_unique_resources(event_log: pd.DataFrame) -> set:
    unique_resources = set(event_log['org:resource'].dropna())
    return unique_resources

def align_date_to_period(date, period, next_period=False):
    if period == 'day':
        aligned_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        aligned_date = (date - timedelta(days=date.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'month':
        aligned_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'year':
        aligned_date = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError("Invalid period. Choose from 'day', 'week', 'month', 'year'.")

    if next_period:
        if period == 'day':
            aligned_date += timedelta(days=1)
        elif period == 'week':
            aligned_date += timedelta(weeks=1)
        elif period == 'month':
            aligned_date += pd.DateOffset(months=1)
        elif period == 'year':
            aligned_date += pd.DateOffset(years=1)

    return aligned_date

def generate_full_time_intervals(start_date_str, end_date_str, period):
    start_date = dt.fromisoformat(start_date_str)
    end_date = dt.fromisoformat(end_date_str)

    intervals = []
    current_start = start_date

    while current_start < end_date:
        current_end = align_date_to_period(current_start, period, next_period=True)

        if current_end > end_date:
            current_end = end_date

        intervals.append((current_start, current_end))
        current_start = current_end

    # Remove the first interval if it's shorter than the others
    if len(intervals) > 1 and (intervals[0][1] - intervals[0][0]) != (intervals[1][1] - intervals[1][0]):
        intervals.pop(0)

    # Remove the last interval if it's shorter than the others
    if len(intervals) > 1 and (intervals[-1][1] - intervals[-1][0]) != (intervals[-2][1] - intervals[-2][0]):
        intervals.pop()

    return intervals

# Convert DataFrame to a JSON string
def df_to_json(df):
    return df.to_json(date_format='iso', orient='split')

# Convert JSON string back to DataFrame
def json_to_df(json_str):
    # Convert the string of JSON to a file-like object
    str_io = StringIO(json_str)
    df = pd.read_json(str_io, orient='split')

    # Convert iso date strings to timestap
    date_columns = [col for col in df.columns if 'date' in col or 'Date' in col or 'time' in col or 'Time' in col]
    for column in date_columns:
        try:
            # Attempt to parse the column as a datetime
            df[column] = pd.to_datetime(df[column], utc=True, errors='raise')
        except (ValueError, TypeError):
            # If parsing fails, we assume it's not a datetime column and move on
            continue
    
    # Ensure datatype of org:resource / undo impicit convertion of pandas
    if 'org:resource' in df.columns:
        df['org:resource'] = df['org:resource'].astype(str)

    return df