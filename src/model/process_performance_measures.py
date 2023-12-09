import pandas as pd
from pandasql import sqldf

def pysqldf(q, local_vars):
    return sqldf(q, local_vars) 

# def sql_to_performance_metric(event_log: pd.DataFrame, sql_query: str, resource_id: str, t_start: pd.Timestamp, t_end: pd.Timestamp) -> float: