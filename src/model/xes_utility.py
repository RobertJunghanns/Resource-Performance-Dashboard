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
    df = pd.read_json(json_str, orient='split')

    # Convert iso date strings to timestap
    for column in df.columns:
        if df[column].dtype == 'object':
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