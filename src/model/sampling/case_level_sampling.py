import pandas as pd
import numpy as np

from enum import Enum
from typing import Callable, List, Any
from model.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp

class ScopeCase(Enum):
    CASE = 1
    INDIVIDUAL = 2
    TOTAL = 3

# E_{T}(t_{1},t_{2})
def get_events_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> pd.DataFrame:
    print('get_events_in_time_frame', event_log)
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


def get_trace(event_log: pd.DataFrame, case_id: str) -> pd.DataFrame:
    trace = event_log.loc[event_log['case:concept:name'] == case_id]
    return trace

def group_equal_timestamp_events(trace: pd.DataFrame) -> pd.DataFrame:

    grouped_complete_events = trace[(trace['lifecycle:transition'] == 'COMPLETE') | (trace['lifecycle:transition'] == 'complete')].groupby(['org:resource', 'time:timestamp'])

    for (resource, timestamp), group in grouped_complete_events:
        if len(group) > 1:
            concept_names_with_start = []
            for concept_name in group['concept:name'].unique():
                if any((trace['concept:name'] == concept_name) & 
                        ((trace['lifecycle:transition'] == 'START') | (trace['lifecycle:transition'] == 'start')) & 
                        (trace['time:timestamp'] < timestamp)):
                    concept_names_with_start.append(concept_name)
            # delete events if they have the same resource and timestamp exept they have a corresponting start event
            trace = trace[~((trace['org:resource'] == resource) & (trace['time:timestamp'] == timestamp)) | trace['concept:name'].isin(concept_names_with_start)]
            # create new grouped event, if nessesary
            if len(concept_names_with_start) < len(group):
                aggregated_name = ' + '.join(list(set(group['concept:name'].unique()) - set(concept_names_with_start)))
                aggregated_event = group.iloc[0].copy()  # Take the first row as base for aggregated event
                aggregated_event['concept:name'] = aggregated_name
                trace = pd.concat([trace, pd.DataFrame([aggregated_event])], ignore_index=True)
        else:
            continue
    
    return trace.sort_values(by='time:timestamp').reset_index(drop=True)  


def add_activity_durations_to_trace(trace: pd.DataFrame) -> pd.DataFrame:

    trace['duration'] = pd.Timedelta(0)

    for index, row in trace.iterrows():
        if row['lifecycle:transition'] == 'COMPLETE' or row['lifecycle:transition'] == 'complete':
            # Option 1: Find a matching START event
            start_event = trace[(trace['concept:name'] == row['concept:name']) & 
                                    ((trace['lifecycle:transition'] == 'START') | (trace['lifecycle:transition'] == 'start')) & 
                                    (trace['time:timestamp'] < row['time:timestamp'])]
            if not start_event.empty:
                start_time = start_event.iloc[-1]['time:timestamp']

            # Option 2: Use the previous COMPLETE event's timestamp
            else:
                prev_complete_event = trace[(trace['time:timestamp'] < row['time:timestamp']) & 
                            ((trace['lifecycle:transition'] == 'COMPLETE') | (trace['lifecycle:transition'] == 'complete'))].tail(1)
                if not prev_complete_event.empty:
                    start_time = prev_complete_event.iloc[0]['time:timestamp']
                # If it's the first event of the trace, duration is 0
                else:
                    start_time = row['time:timestamp']  

            trace.at[index, 'duration'] = row['time:timestamp'] - start_time

    return trace

def prepare_trace(trace: pd.DataFrame) -> pd.DataFrame:
    trace_grouped = group_equal_timestamp_events(trace)
    trace_grouped_duration = add_activity_durations_to_trace(trace_grouped)
    trace_grouped_duration_complete = trace_grouped_duration[(trace_grouped_duration['lifecycle:transition'] == 'COMPLETE') | (trace_grouped_duration['lifecycle:transition'] == 'complete')]
    trace_grouped_duration_complete_cleaned = trace_grouped_duration_complete.dropna(subset=['org:resource'])
    return trace_grouped_duration_complete_cleaned

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
        t1 = get_earliest_timestamp(trace)

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
def sample_regression_data_case(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp, scope: ScopeCase, rbi_function: Callable, performance_function: Callable, additional_rbi_arguments: List[Any] = [], additional_performance_arguments: List[Any] = [], individual_scope = pd.Timedelta(0)):
    case_ids = get_caseids_in_time_frame(event_log, t_start, t_end)

    rbi_values = np.array([])
    perf_values = np.array([])
    
    for case_id in case_ids:
        print(case_id)
        rbi_values = np.append(rbi_values, get_independent_variable_case(event_log, case_id, scope, rbi_function, *additional_rbi_arguments, individual_scope=individual_scope))
        perf_values = np.append(perf_values, get_dependent_variable_case(event_log, case_id, performance_function, *additional_performance_arguments))

    return rbi_values, perf_values
        
