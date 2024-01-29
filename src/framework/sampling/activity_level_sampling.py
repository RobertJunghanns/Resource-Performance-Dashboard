import pandas as pd
import numpy as np

from enum import Enum
from typing import Callable, List, Any
from framework.utility.sampling_utility import get_trace, get_n_events, prepare_trace
from framework.utility.xes_utility import get_earliest_timestamp

class ScopeActivity(Enum):
    ACTIVITY = 1
    INDIVIDUAL = 2
    TOTAL = 3


# E_{TA}(t_{1}, t_{2}, [a, v])
def get_included_events(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, filter_event_attribute: str = None, filter_event_value = None):
    event_log = event_log[
        (event_log['lifecycle:transition'].isin(['complete', 'COMPLETE'])) &
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] < t_end)
    ]
    if filter_event_attribute is not None and filter_event_value is not None and filter_event_attribute in event_log.columns:
        event_log = event_log[event_log[filter_event_attribute] == filter_event_value]
    
    return event_log
    
# IV(c)
def get_independent_variable_activity(event_log: pd.DataFrame, event: pd.Series, activity_duration: pd.Timedelta, scope: ScopeActivity, rbi_function: Callable, *args, individual_scope = pd.Timedelta(0)):    
    t2 = event['time:timestamp']
    if scope == ScopeActivity.ACTIVITY:
        t1 = event['time:timestamp'] - activity_duration
    elif scope == ScopeActivity.INDIVIDUAL:
        t1 = event['time:timestamp'] - activity_duration - individual_scope
    elif scope == ScopeActivity.TOTAL:
        t1 = get_earliest_timestamp(event_log)
    else:
        raise ValueError(f"ScopeActivity not found.")

    activity_resource_id = event['org:resource']
    rbi_value = rbi_function(event_log, t1, t2, activity_resource_id, *args)

    return rbi_value

def get_dependent_variable_activity(event: pd.Series, performance_function: Callable, *args):
    return performance_function(event, *args)

# [(IV, DV)] for all c element C_{T}(t_{1},t_{2})
def sample_regression_data_activity(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, filter_event_attribute: str, filter_event_value: str, activity_limit: int, seed: int,  scope: ScopeActivity, rbi_function: Callable, performance_function: Callable, additional_rbi_arguments: List[Any] = [], additional_performance_arguments: List[Any] = [], individual_scope = pd.Timedelta(0)):
    included_events = get_included_events(event_log, t_start, t_end, filter_event_attribute, filter_event_value)
    included_events = get_n_events(included_events, activity_limit, seed)

    rbi_values = np.array([])
    perf_values = np.array([])
    
    for _, event in included_events.iterrows():
        # get the trace for an activity duration analysis (prepare_trace)
        trace = get_trace(event_log, event['case:concept:name'])
        trace_prepared = prepare_trace(trace)
        activity_duration = pd.Timedelta(0)

         # find the prepared event in the trace and extract duration
        matching_events_prepared = trace_prepared[trace_prepared['concept:name'].str.contains(event['concept:name']) & (trace_prepared['time:timestamp'] == event['time:timestamp'])]
        activity_duration = matching_events_prepared.iloc[0]['duration']

        rbi_values = np.append(rbi_values, get_independent_variable_activity(event_log, event, activity_duration, scope, rbi_function, *additional_rbi_arguments, individual_scope=individual_scope))
        perf_values = np.append(perf_values, get_dependent_variable_activity(event, performance_function, activity_duration, *additional_performance_arguments))

    return rbi_values, perf_values
