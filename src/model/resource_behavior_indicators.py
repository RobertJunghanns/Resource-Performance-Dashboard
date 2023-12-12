import pandas as pd
from pandasql import sqldf
from pm4py.algo.organizational_mining.resource_profiles import algorithm
import statistics

def pysqldf(q, local_vars):
    return sqldf(q, local_vars)

def sql_to_rbi(event_log: pd.DataFrame, sql_query: str, resource_id: str, t_start: pd.Timestamp, t_end: pd.Timestamp) -> float:

    event_log = event_log[
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] <= t_end)
    ]

    sql_query = sql_query.replace('resource_id', resource_id)

    result = pysqldf(sql_query, {'event_log': event_log}).iloc[0, 0]

    if not result:
        result = 0

    return result

def rbi_distinct_activities(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.activity_completions(event_log, t_start, t_end, resource_id)

def rbi_activity_completions(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.activity_completions(event_log, t_start, t_end, resource_id)

def rbi_activity_fequency(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, concept_name: str) -> float:
    return algorithm.activity_frequency(event_log, t_start, t_end, resource_id, concept_name)

def rbi_activity_completions(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.activity_completions(event_log, t_start, t_end, resource_id)

def rbi_case_completions(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.case_completions(event_log, t_start, t_end, resource_id)

def rbi_fraction_case_completions(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.fraction_case_completions(event_log, t_start, t_end, resource_id)

def rbi_average_workload(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.average_workload(event_log, t_start, t_end, resource_id)

def rbi_multitasking(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.multitasking(event_log, t_start, t_end, resource_id)

def rbi_average_duration_activity(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, concept_name: str) -> float:
    return algorithm.average_duration_activity(event_log, t_start, t_end, resource_id, concept_name)

def rbi_average_case_duration(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    try:
        return algorithm.average_case_duration(event_log, t_start, t_end, resource_id)
    except statistics.StatisticsError:
        return None

def rbi_interaction_two_resources(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, interaction_resource_id: str) -> float:
    return algorithm.interaction_two_resources(event_log, t_start, t_end, resource_id, interaction_resource_id)

def rbi_social_position(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.social_position(event_log, t_start, t_end, resource_id)

# def rbi_distinct_activities(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
#     return sql_to_rbi(
#         sql_query = f"""
#         SELECT COUNT(DISTINCT [concept:name])
#         FROM event_log
#         WHERE [org:resource] = '{resource_id}'
#         """,
#         event_log = event_log,
#         t_start = t_start,
#         t_end = t_end,
#         resource_id = resource_id
#     )

# def rbi_activity_completions(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
#     return sql_to_rbi(
#         sql_query = f"""
#         SELECT COUNT([concept:name])
#         FROM event_log
#         WHERE [org:resource] = '{resource_id}'
#         """,
#         event_log = event_log,
#         t_start = t_start,
#         t_end = t_end,
#         resource_id = resource_id
#     )

# def rbi_activity_fequency(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, concept_name: str) -> float:
#     return sql_to_rbi(
#         sql_query = f"""
#         SELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)
#         FROM (
#             SELECT
#                 (SELECT COUNT([concept:name])
#                 FROM event_log
#                 WHERE [org:resource] = '{resource_id}' AND [concept:name] = '{concept_name}') AS activity,
#                 (SELECT COUNT([concept:name])
#                 FROM event_log
#                 WHERE [org:resource] = '{resource_id}') AS all_activities         
#         ) AS count
#         """,
#         event_log = event_log,
#         t_start = t_start,
#         t_end = t_end,
#         resource_id = resource_id
#     )