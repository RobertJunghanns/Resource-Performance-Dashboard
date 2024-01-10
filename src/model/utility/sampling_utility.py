import pandas as pd
import numpy as np

# get a lower number of ids to reduce case sampling time
def get_n_case_ids(case_ids, n_cases, seed=999):
    np.random.seed(seed)
    if len(case_ids) > n_cases:
        return np.random.choice(case_ids, size=n_cases, replace=False)
    else:
        return case_ids
    
# get a lower number of activities to reduce case sampling time
def get_n_events(event_log, n_events, seed=999):
    if len(event_log) > n_events:
        return event_log.sample(n=n_events, random_state=seed)
    else:
        return event_log


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