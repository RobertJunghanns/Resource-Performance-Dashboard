import pandas as pd
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

def get_column_names(event_log: pd.DataFrame):
    return list(event_log.columns)

def count_unique_cases(df, case_id_column='case:concept:name'):
    if case_id_column in df.columns:
        return df[case_id_column].nunique()
    else:
        raise ValueError(f"Column '{case_id_column}' not found in DataFrame")
    
def count_completed_events(df, lifecycle_column='lifecycle:transition'):
    if lifecycle_column in df.columns:
        return len(df[df[lifecycle_column].isin(['complete', 'COMPLETE'])])
    else:
        raise ValueError(f"Column '{lifecycle_column}' not found in DataFrame")
