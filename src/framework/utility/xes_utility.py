import config
import pandas as pd

def get_earliest_timestamp(event_log: pd.DataFrame) -> pd.Timestamp:
    earliest_timestamp = event_log[config.timestamp_col].min()
    return earliest_timestamp

def get_latest_timestamp(event_log: pd.DataFrame) -> pd.Timestamp:
    latest_timestamp = event_log[config.timestamp_col].max()
    return latest_timestamp

def get_unique_resources(event_log: pd.DataFrame) -> set:
    unique_resources = set(event_log[config.resource_col].dropna())
    return unique_resources

def get_column_names(event_log: pd.DataFrame):
    return list(event_log.columns)

def count_unique_cases(df, case_id_column=config.case_col):
    if case_id_column in df.columns:
        return df[case_id_column].nunique()
    else:
        raise ValueError(f"Column '{case_id_column}' not found in DataFrame")
    
def count_completed_events(df, lifecycle_column=config.lifecycle_col):
    if lifecycle_column in df.columns:
        return len(df[df[lifecycle_column].isin(['complete', 'COMPLETE'])])
    else:
        raise ValueError(f"Column '{lifecycle_column}' not found in DataFrame")
