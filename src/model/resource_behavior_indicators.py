import pandas as pd
from pandasql import sqldf
from pm4py.algo.organizational_mining.resource_profiles import algorithm
from pm4py.objects.log.obj import EventLog
from pathlib import Path
import pm4py

def pysqldf(q, local_vars):
    return sqldf(q, local_vars)

def sql_to_rbi(sql_query: str, event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:

    event_log = event_log[
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] <= t_end)
    ]

    sql_query = sql_query.replace('resource_id', resource_id)

    result = pysqldf(sql_query, {'event_log': event_log})
    distinct_activities_count = result.iloc[0, 0]

    if not distinct_activities_count: 
        distinct_activities_count = 0

    return distinct_activities_count

def rbi_distinct_activities_pika(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    #current_file_path = Path(__file__).resolve().parent.parent
    #file_path = str(current_file_path / 'data' / ('BPIC15_1_1' + '.xes'))
    #df_event_log = pm4py.read_xes(file_path)
    print(algorithm.activity_completions(event_log, "2010-11-01 00:00:00", "2015-06-01 00:00:00", "560872"))
    return algorithm.activity_completions(event_log, "2010-11-01 00:00:00", "2015-06-01 00:00:00", resource_id)
    #return algorithm.distinct_activities(event_log, t_start, t_end, resource_id)

def rbi_distinct_activities(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return sql_to_rbi(
        sql_query = f"""
        SELECT COUNT(DISTINCT [concept:name])
        FROM event_log
        WHERE [org:resource] = '{resource_id}'
        """,
        event_log = event_log,
        t_start = t_start,
        t_end = t_end,
        resource_id = resource_id
    )

def rbi_activity_completions(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return sql_to_rbi(
        sql_query = f"""
        SELECT COUNT([concept:name])
        FROM event_log
        WHERE [org:resource] = '{resource_id}'
        """,
        event_log = event_log,
        t_start = t_start,
        t_end = t_end,
        resource_id = resource_id
    )

def rbi_activity_fequency(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, concept_name: str) -> float:
    return sql_to_rbi( #
        sql_query = f"""
        SELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)
        FROM (
            SELECT
                (SELECT COUNT([concept:name])
                FROM event_log
                WHERE [org:resource] = '{resource_id}' AND [concept:name] = '{concept_name}') AS activity,
                (SELECT COUNT([concept:name])
                FROM event_log
                WHERE [org:resource] = '{resource_id}') AS all_activities         
        ) AS count
        """,
        event_log = event_log,
        t_start = t_start,
        t_end = t_end,
        resource_id = resource_id
    )