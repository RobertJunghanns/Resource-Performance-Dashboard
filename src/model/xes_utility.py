import pandas as pd

def get_earliest_timestamp(event_log: pd.DataFrame) -> pd.Timestamp:
    earliest_timestamp = event_log['time:timestamp'].min()
    return earliest_timestamp

def get_latest_timestamp(event_log: pd.DataFrame) -> pd.Timestamp:
    latest_timestamp = event_log['time:timestamp'].max()
    return latest_timestamp

def get_unique_resources(event_log: pd.DataFrame) -> set:
    unique_resources = set(event_log['org:resource'].dropna())
    return unique_resources

# Convert DataFrame to a JSON string
def df_to_json(df):
    return df.to_json(date_format='iso', orient='split')

# Convert JSON string back to DataFrame
def json_to_df(json_str):
    return pd.read_json(json_str, orient='split')