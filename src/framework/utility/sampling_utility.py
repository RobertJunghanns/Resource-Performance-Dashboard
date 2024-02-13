import pandas as pd
import numpy as np

# get a lower number of ids to reduce case sampling time
def get_n_case_ids(case_ids, n_cases, seed=999):
    np.random.seed(seed)
    if len(case_ids) > n_cases:
        return np.random.choice(case_ids, size=n_cases, replace=False)
    else:
        return case_ids
    
# get a lower number of activities to reduce activity sampling time
def get_n_events(event_log, n_events, seed=999):
    # Filter out rows where 'org:resource' is None or NaN
    filtered_event_log = event_log.dropna(subset=['org:resource'])
    
    if len(filtered_event_log) > n_events:
        # Sample n_events from the filtered DataFrame
        return filtered_event_log.sample(n=n_events, random_state=seed)
    else:
        # If there aren't enough events after filtering, return the filtered DataFrame
        return filtered_event_log


def get_trace(event_log: pd.DataFrame, case_id: str) -> pd.DataFrame:
    trace = event_log.loc[event_log['case:concept:name'] == case_id]
    return trace

def group_equal_timestamp_events(trace: pd.DataFrame) -> pd.DataFrame:

    grouped_complete_events = trace[(trace['lifecycle:transition'] == 'COMPLETE') | (trace['lifecycle:transition'] == 'complete')].groupby(['org:resource', 'time:timestamp'])

    for (resource, timestamp), group in grouped_complete_events:
        if len(group) > 1:
            concept_names_with_start = []
            # check if any of the grouped events has a start event
            for concept_name in group['concept:name']:
                if any((trace['concept:name'] == concept_name) & 
                        (trace['lifecycle:transition'].str.lower() == 'start') & 
                        (trace['time:timestamp'] < timestamp)):
                    concept_names_with_start.append(concept_name)
            # delete events if they have the same resource and timestamp exept they have a corresponting start event
            trace = trace[~((trace['org:resource'] == resource) & (trace['time:timestamp'] == timestamp)) | trace['concept:name'].isin(concept_names_with_start)]
            # create new grouped event, if nessesary
            if len(concept_names_with_start) < len(group):
                aggregated_name = ' + '.join([name for name in group['concept:name'].unique() if name not in concept_names_with_start])
                aggregated_event = group.iloc[0].copy()  # Take the first row as base for aggregated event
                aggregated_event['concept:name'] = aggregated_name
                trace = pd.concat([trace, pd.DataFrame([aggregated_event])], ignore_index=True)
        else:
            continue
    
    return trace.sort_values(by='time:timestamp').reset_index(drop=True)  


def add_activity_durations_to_trace(trace: pd.DataFrame) -> pd.DataFrame:
    # trace copy to delete used START events
    trace_copy = trace.copy()
    # set default activity duration
    trace['duration'] = pd.Timedelta(0)

    for index, row in trace.iterrows():
        if row['lifecycle:transition'] == 'COMPLETE' or row['lifecycle:transition'] == 'complete':
            # For Option 1: find start event in trace_copy that deletes every used START event
            start_event_copy = trace_copy[(trace_copy['concept:name'] == row['concept:name']) & 
                                    ((trace_copy['lifecycle:transition'] == 'START') | (trace_copy['lifecycle:transition'] == 'start')) & 
                                    (trace_copy['time:timestamp'] < row['time:timestamp'])]
            # For Option 2: find any start event even if it is used before
            start_event = trace[(trace['concept:name'] == row['concept:name']) & 
                                    ((trace['lifecycle:transition'] == 'START') | (trace['lifecycle:transition'] == 'start')) & 
                                    (trace['time:timestamp'] < row['time:timestamp'])]
            
            # Option 1: Find the FIRST matching START event
            if not start_event_copy.empty:
                # take the first matching START event, that no COMPLETE event has matched before 
                start_time = start_event_copy.iloc[0]['time:timestamp']
                # Delete the first matching START event from trace_copy, such that no other COMPLETE event can match the START event
                trace_copy.drop(start_event_copy.index[0], inplace=True)
            
            # Option 2: Find the ANY matching START event
            elif not start_event.empty:
                # take the last matching START event, eaven if some COMPLETE event has already matched
                start_time = start_event.iloc[-1]['time:timestamp']

            # Option 3: Use the previous COMPLETE event's timestamp
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