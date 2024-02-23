import time
import pandas as pd
import numpy as np

from enum import Enum
from typing import Callable, List, Any
from framework.sampling.activity_duration_estimation import get_trace, prepare_trace, get_n_case_ids
from framework.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp

class ScopeCase(Enum):
    CASE = 1
    INDIVIDUAL = 2
    TOTAL = 3

# E_{T}(t_{1},t_{2})
def get_events_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> pd.DataFrame:
    return event_log[
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] < t_end)
    ]

# E_{¬T}(t_{1},t_{2})
def get_events_not_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> pd.DataFrame:
    return event_log[
        (event_log['time:timestamp'] < t_start) |
        (event_log['time:timestamp'] >= t_end)
    ]

# C_{T}(t_{1},t_{2}) = ids of fully contained cases
def get_caseids_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> np.array:
    events_in_time_frame = get_events_in_time_frame(event_log, t_start, t_end)
    events_not_in_time_frame = get_events_not_in_time_frame(event_log, t_start, t_end)

    cases_ids_in_time_frame = set(events_in_time_frame['case:concept:name'])
    cases_ids_not_in_time_frame = set(events_not_in_time_frame['case:concept:name'])

    return np.array(list(cases_ids_in_time_frame - cases_ids_not_in_time_frame))

# R_{C}(c)
def get_participating_resources(trace: pd.DataFrame) -> np.ndarray:
    return trace['org:resource'].dropna().unique()

# PS(c,r)
def participation_share(trace_prepared: pd.DataFrame, resource_id: str) -> float:
    duration_sum = trace_prepared['duration'].sum()
    resource_duration_sum = trace_prepared[trace_prepared['org:resource'] == resource_id]['duration'].sum()

    return resource_duration_sum/duration_sum

# IV(c)
def get_independent_variable_case(event_log: pd.DataFrame, case_id: str, scope: ScopeCase, rbi_function: Callable, *args, individual_scope = pd.Timedelta(0)):
    trace = get_trace(event_log, case_id)
    trace_prepared = prepare_trace(trace)

    t2 = get_latest_timestamp(trace)
    if scope == ScopeCase.CASE:
        t1 = get_earliest_timestamp(trace)
    elif scope == ScopeCase.INDIVIDUAL:
        t1 = get_earliest_timestamp(trace) - individual_scope
    elif scope == ScopeCase.TOTAL:
        t1 = get_earliest_timestamp(event_log) 
    else:
        raise ValueError(f"ScopeCase not found.")

    weighted_avg = 0

    resource_ids = get_participating_resources(trace)
    for resource_id in resource_ids:
        ps = participation_share(trace_prepared, resource_id)
        rbi_value = rbi_function(event_log, t1, t2, resource_id, *args)
        weighted_avg += rbi_value * ps

    return weighted_avg

# DV(c)
def get_dependent_variable_case(event_log: pd.DataFrame, case_id: str, performance_function: Callable, *args):
    trace = get_trace(event_log, case_id)
    return performance_function(trace, *args)

# [(IV, DV)] for all c element C_{T}(t_{1},t_{2})
def sample_regression_data_case(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, case_limit: int, seed: int, scope: ScopeCase, rbi_function: Callable, performance_function: Callable, additional_rbi_arguments: List[Any] = [], additional_performance_arguments: List[Any] = [], individual_scope = pd.Timedelta(0)):
    case_ids = get_caseids_in_time_frame(event_log, t_start, t_end)
    case_ids = get_n_case_ids(case_ids, case_limit, seed)

    rbi_values = np.array([])
    perf_values = np.array([])

    for case_id in case_ids:
        rbi_values = np.append(rbi_values, get_independent_variable_case(event_log, case_id, scope, rbi_function, *additional_rbi_arguments, individual_scope=individual_scope))
        perf_values = np.append(perf_values, get_dependent_variable_case(event_log, case_id, performance_function, *additional_performance_arguments))

    return rbi_values, perf_values
        
