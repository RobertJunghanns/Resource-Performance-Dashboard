import pandas as pd
import numpy as np

from enum import Enum
from typing import Callable, List, Any
from model.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp

class ScopeActivity(Enum):
    ACTIVITY = 1
    INDIVIDUAL = 2
    TOTAL = 3

def get_included_events(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, event_attribute: str = None, event_attribute_value = None):
    event_log = event_log[
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] < t_end)
    ]

    if event_attribute is not None and event_attribute_value is not None and event_attribute in event_log.columns:
        event_log = event_log[event_log[event_attribute] == event_attribute_value]
    
    return event_log

# Prepare all cases in timeframe with duration of completed event

# IV(c)
def get_independent_variable_activity(event_log: pd.DataFrame, case_id: str, scope: ScopeActivity, rbi_function: Callable, *args, individual_scope = pd.Timedelta(0)):    
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
        t1 = get_earliest_timestamp(trace)

    weighted_avg = 0

    resource_ids = get_participating_resources(trace)
    for resource_id in resource_ids:
        ps = participation_share(trace_prepared, resource_id)
        rbi_value = rbi_function(event_log, t1, t2, resource_id, *args)

        weighted_avg += rbi_value * ps

    return weighted_avg
