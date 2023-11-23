import pandas as pd
from pandasql import sqldf

pysqldf = lambda q: sqldf(q, globals())

def rbi_distinct_activities(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> int:
    # Filter the event log for the given resource and time period
    filtered_log = event_log[
        (event_log['org:resource'] == resource_id) &
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] <= t_end)
    
    
    sql_query = f"""
    SELECT COUNT(DISTINCT [concept:name]) as distinct_activities_count
    FROM event_log
    WHERE [org:resource] = '{resource_id}' 
    AND [time:timestamp] BETWEEN '{t_start}' AND '{t_end}'
    """]
    
    # Count the number of distinct activities
    distinct_activities_count = filtered_log['concept:name'].nunique()
    
    return distinct_activities_count