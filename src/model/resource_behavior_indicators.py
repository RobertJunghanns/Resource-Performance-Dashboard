import pandas as pd
from pandasql import sqldf

def pysqldf(q, local_vars):
    return sqldf(q, local_vars)

def sql_to_rbi(sql_query: str, event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    # Filter the event log for the given resource and time period
    filtered_log = event_log[
        (event_log['org:resource'] == resource_id) &
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] <= t_end)
    ]

    result = pysqldf(sql_query, {'filtered_log': filtered_log})
    distinct_activities_count = result.iloc[0, 0]
    
    return distinct_activities_count

def rbi_distinct_activities(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return sql_to_rbi(
        sql_query = f"""
        SELECT COUNT(DISTINCT [concept:name])
        FROM filtered_log
        """,
        event_log = event_log,
        t_start = t_start,
        t_end = t_end,
        resource_id = resource_id
    )