import config
import time
import pandas as pd
import numpy as np

from enum import Enum
from typing import Callable, List, Any
from framework.sampling.activity_duration_estimation import get_trace, get_n_events, prepare_trace
from framework.utility.xes_utility import get_earliest_timestamp

class ScopeActivity(Enum):
    ACTIVITY = 1
    INDIVIDUAL = 2
    TOTAL = 3


# E_{TA}(t_{1}, t_{2}, [a, v])
def filter_event_log(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, filter_event_attribute: str = None, filter_event_value = None):
    event_log = event_log[
        (event_log[config.lifecycle_col].isin(['complete', 'COMPLETE'])) &
        (event_log[config.timestamp_col] >= t_start) &
        (event_log[config.timestamp_col] < t_end)
    ]
    if filter_event_attribute is not None and filter_event_value is not None and filter_event_attribute in event_log.columns:
        event_log = event_log[event_log[filter_event_attribute] == filter_event_value]
    
    return event_log
    
# IV(c, [p_1...p_n])
def get_independent_variable_activity(event_log: pd.DataFrame, event: pd.Series, activity_duration: pd.Timedelta, scope: ScopeActivity, rbi_function: Callable, *args, individual_scope = pd.Timedelta(0)):    
    # add millisecond to t2 to use pm4py RBIs with <=t2 not <t2
    t2 = event[config.timestamp_col] #+ timedelta(milliseconds=1)
    if scope == ScopeActivity.ACTIVITY:
        t1 = event[config.timestamp_col] - activity_duration
    elif scope == ScopeActivity.INDIVIDUAL:
        t1 = event[config.timestamp_col] - individual_scope
    elif scope == ScopeActivity.TOTAL:
        t1 = get_earliest_timestamp(event_log)
    else:
        raise ValueError(f"ScopeActivity not found.")

    activity_resource_id = event[config.resource_col]
    rbi_value = rbi_function(event_log, t1, t2, activity_resource_id, *args)

    return rbi_value

def get_dependent_variable_activity(event: pd.Series, performance_function: Callable, *args):
    return performance_function(event, *args)

# [(IV, DV)] for all c element C_{T}(t_{1},t_{2})
def sample_regression_data_activity(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, filter_event_attribute: str, filter_event_value: str, activity_limit: int, seed: int, scope: ScopeActivity, rbi_function: Callable, performance_function: Callable, additional_rbi_arguments: List[Any] = [], additional_performance_arguments: List[Any] = [], individual_scope = pd.Timedelta(0)):
    included_events = filter_event_log(event_log, t_start, t_end, filter_event_attribute, filter_event_value)
    n_Events = get_n_events(included_events, activity_limit, seed)

    rbi_values = np.array([])
    perf_values = np.array([])

    # information for lookup
    case_id_info = np.array([])
    activity_info = np.array([])
    resource_info = np.array([])

    # information runtime
    iteration_times = np.array([])
    total_events = n_Events.shape[0]
    iteration_count = 0
    
    for _, event in n_Events.iterrows():
        # information for runtime
        start_time = time.time()

        # get the trace for an activity duration analysis (prepare_trace)
        trace = get_trace(event_log, event[config.case_col])
        trace_prepared = prepare_trace(trace)

         # find the prepared event in the trace and extract duration
        activity_duration = pd.Timedelta(0)
        matching_events_prepared = trace_prepared[trace_prepared[config.activity_col].str.contains(event[config.activity_col]) & (trace_prepared[config.timestamp_col] == event[config.timestamp_col])]
        activity_duration = matching_events_prepared.iloc[0]['duration']

        rbi_values = np.append(rbi_values, get_independent_variable_activity(event_log, event, activity_duration, scope, rbi_function, *additional_rbi_arguments, individual_scope=individual_scope))
        perf_values = np.append(perf_values, get_dependent_variable_activity(event, performance_function, activity_duration, *additional_performance_arguments))

        # information for lookup
        case_id_info = np.append(case_id_info, event[config.case_col])
        activity_info = np.append(activity_info, event[config.activity_col])
        resource_info = np.append(resource_info, event[config.resource_col])

        # information for runtime
        end_time = time.time()
        iteration_time = end_time - start_time
        iteration_times = np.append(iteration_times, iteration_time)
        iteration_count += 1

        # print progress
        if iteration_count % 10 == 0:
            print(f"Progress: {iteration_count}/{total_events}. Average time per iteration: {(np.average(iteration_times)):.4f} seconds.")

    # information for lookup
    lookup_information = {
        'case_id': case_id_info,
        'activity_id': activity_info,
        'resource': resource_info
    }
    return rbi_values, perf_values, lookup_information
