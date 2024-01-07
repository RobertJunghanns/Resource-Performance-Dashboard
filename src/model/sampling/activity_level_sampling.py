import pandas as pd
import numpy as np

from enum import Enum
from typing import Callable, List, Any
from model.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp

class ScopeActivity(Enum):
    ACTIVITY = 1
    INDIVIDUAL = 2
    TOTAL = 3


# E_{TA}(t_{1}, t_{2}, [a, v])
def get_included_events(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, event_attribute: str = None, event_attribute_value = None):
    event_log = event_log[
        (event_log['lifecycle:transition'].isin(['complete', 'COMPLETE'])) &
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] < t_end)
    ]

    if event_attribute is not None and event_attribute_value is not None and event_attribute in event_log.columns:
        event_log = event_log[event_log[event_attribute] == event_attribute_value]
    
    return event_log

# get a lower number of activities to reduce case sampling time
def get_n_events(event_log, n_events, seed=999):
    if len(event_log) > n_events:
        return event_log.sample(n=n_events, random_state=seed)
    else:
        return event_log

# [(IV, DV)] for all c element C_{T}(t_{1},t_{2})
def sample_regression_data_activity(event_log: pd.DataFrame, activity_limit: int, seed: int, t_start: pd.Timestamp, t_end: pd.Timestamp, scope: ScopeActivity): #, rbi_function: Callable, performance_function: Callable, additional_rbi_arguments: List[Any] = [], additional_performance_arguments: List[Any] = [], individual_scope = pd.Timedelta(0)
    included_events = get_included_events(event_log, t_start, t_end)
    included_events = get_n_events(included_events, activity_limit, seed)

    pd.set_option('display.max_columns', None)

    print(included_events)

    rbi_values = np.array([])
    perf_values = np.array([])
    
    # for index, event in included_events.iterrows():
    #     rbi_values = np.append(rbi_values, get_independent_variable_case(event_log, case_id, scope, rbi_function, *additional_rbi_arguments, individual_scope=individual_scope))
    #     perf_values = np.append(perf_values, get_dependent_variable_case(event_log, case_id, performance_function, *additional_performance_arguments))

    return rbi_values, perf_values
