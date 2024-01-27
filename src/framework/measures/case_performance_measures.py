import pandas as pd
from pandasql import sqldf
from framework.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp

def pysqldf(q, local_vars):
    return sqldf(q, local_vars) 

def sql_to_case_performance_metric(trace: pd.DataFrame, sql_query: str) -> float:
    result = pysqldf(sql_query, {'trace': trace}).iloc[0, 0]

    if not result:
        result = 0

    return result


def case_duration(trace: pd.DataFrame) -> float:
    earliest_timestamp = get_earliest_timestamp(trace)
    latest_timestamp = get_latest_timestamp(trace)
    diff_minutes = (latest_timestamp - earliest_timestamp).total_seconds() / 60
    return diff_minutes