import time
import pandas as pd
import numpy as np

from enum import Enum
from datetime import timedelta
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
        (event_log['time:timestamp'] <= t_end)
    ]

# E_{¬T}(t_{1},t_{2})
def get_events_not_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> pd.DataFrame:
    return event_log[
        (event_log['time:timestamp'] < t_start) |
        (event_log['time:timestamp'] > t_end)
    ]

# C_{T}(t_{1},t_{2}) = ids of fully contained cases
def get_caseids_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> np.array:
    events_in_time_frame = get_events_in_time_frame(event_log, t_start, t_end)
    events_not_in_time_frame = get_events_not_in_time_frame(event_log, t_start, t_end)

    cases_ids_in_time_frame = set(events_in_time_frame['case:concept:name'])
    cases_ids_not_in_time_frame = set(events_not_in_time_frame['case:concept:name'])

    return np.array(list(cases_ids_in_time_frame - cases_ids_not_in_time_frame))

# Only in Dashboard: extra filter for specific filter function to drill down into cases (e.g. trace variants of BPIC'12)
def get_filtered_caseids(event_log: pd.DataFrame, case_ids_tf, filter_function: callable) -> pd.DataFrame:
    event_log = event_log[event_log['case:concept:name'].isin(case_ids_tf)]
    event_log_filtered = filter_function(event_log)
    case_ids_filtered = event_log_filtered['case:concept:name'].unique()
    return case_ids_filtered

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

    # add millisecond to t2 to use pm4py RBIs effectivly with <=t2 not <t2
    t2 = get_latest_timestamp(trace) #+ timedelta(milliseconds=1)
    if scope == ScopeCase.CASE:
        t1 = get_earliest_timestamp(trace)
    elif scope == ScopeCase.INDIVIDUAL:
        t1 = get_latest_timestamp(trace) - individual_scope
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

    participating_resources_str = ','.join(resource_ids)

    return weighted_avg, participating_resources_str

# DV(c)
def get_dependent_variable_case(event_log: pd.DataFrame, case_id: str, performance_function: Callable, *args):
    trace = get_trace(event_log, case_id)
    return performance_function(trace, *args)

# [(IV, DV)] for all c element C_{T}(t_{1},t_{2})
def sample_regression_data_case(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, case_limit: int, seed: int, scope: ScopeCase, rbi_function: Callable, performance_function: Callable, additional_rbi_arguments: List[Any] = [], additional_performance_arguments: List[Any] = [], individual_scope = pd.Timedelta(0), filter_function: callable = lambda log: log):
    # filter by time frame
    case_ids_tf = get_caseids_in_time_frame(event_log, t_start, t_end)
    # filter by case ids in time frame by custom case filter function
    case_ids_filtered = get_filtered_caseids(event_log, case_ids_tf, filter_function)
    # get max n case ids
    case_ids = get_n_case_ids(case_ids_filtered, case_limit, seed)

    rbi_values = np.array([])
    perf_values = np.array([])

    # information for lookup
    case_id_info = np.array([])
    resource_info = np.array([])
    trace_info = np.array([])

    # information runtime
    iteration_times = np.array([])

    total_cases = len(case_ids)
    for index, case_id in enumerate(case_ids): 
        start_time = time.time()

        rbi_value, participating_resources_str = get_independent_variable_case(event_log, case_id, scope, rbi_function, *additional_rbi_arguments, individual_scope=individual_scope)
        perf_value = get_dependent_variable_case(event_log, case_id, performance_function, *additional_performance_arguments)

        rbi_values = np.append(rbi_values, rbi_value)
        perf_values = np.append(perf_values, perf_value)

        # information for lookup
        case_id_info = np.append(case_id_info, case_id)
        resource_info = np.append(resource_info, participating_resources_str)
        activities = event_log[event_log['case:concept:name'] == case_id]['concept:name'].tolist()
        if len(activities) > 7:
            # Show first 3 activities, placeholder for the skipped ones, and the last 3 activities
            skipped_activities = len(activities) - 6
            trace_str = '->'.join(activities[:3] + [f"...{skipped_activities} activities..."] + activities[-3:])
        else:
            trace_str = '->'.join(activities)
        trace_info = np.append(trace_info, trace_str)

        # information runtime
        end_time = time.time()
        iteration_time = end_time - start_time
        iteration_times = np.append(iteration_times, iteration_time)
        
        if (index + 1) % 10 == 0:
            print(f"Progress: {index + 1}/{total_cases}. Average time per iteration: {(np.average(iteration_times)):.4f} seconds.")
    
    # information for lookup
    lookup_information = {
        'case_id': case_id_info,
        'trace': trace_info,
        'resources': resource_info
    }

    return rbi_values, perf_values, lookup_information
        
