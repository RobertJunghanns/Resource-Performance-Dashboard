import config
import pandas as pd
from pandasql import sqldf
from pm4py.algo.organizational_mining.resource_profiles import algorithm

def pysqldf(q, local_vars):
    return sqldf(q, local_vars)

def sql_to_rbi(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, sql_query: str) -> float:

    event_log = event_log[
        (event_log[config.timestamp_col] >= t_start) &
        (event_log[config.timestamp_col] < t_end)
    ]
    sql_query = sql_query.replace('{r}', resource_id)

    result = pysqldf(sql_query, {'event_log': event_log})

    try:
        result_num = result.iloc[0, 0]
    except Exception as e:
        raise ValueError("SQL query result is empty. This is likely due to a missing aggregation function to return a numeric value.") from e

    if not isinstance(result_num, (int, float)):
        raise ValueError("SQL query result is not numeric.")

    return float(result_num)

def rbi_distinct_activities(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.distinct_activities(event_log, t_start, t_end, resource_id)

def rbi_activity_completions(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.activity_completions(event_log, t_start, t_end, resource_id)

def rbi_activity_fequency(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, concept_name: str) -> float:
    return algorithm.activity_frequency(event_log, t_start, t_end, resource_id, concept_name)

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

def rbi_interaction_two_resources(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str, interaction_resource_id: str) -> float:
    return algorithm.interaction_two_resources(event_log, t_start, t_end, resource_id, interaction_resource_id)

def rbi_social_position(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, resource_id: str) -> float:
    return algorithm.social_position(event_log, t_start, t_end, resource_id)