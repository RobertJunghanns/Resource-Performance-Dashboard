import config
import pandas as pd
import numpy as np

def get_trace(event_log: pd.DataFrame, case_id: str) -> pd.DataFrame:
    trace = event_log.loc[event_log[config.case_col] == case_id]
    return trace

def group_equal_timestamp_events(trace: pd.DataFrame) -> pd.DataFrame:

    grouped_complete_events = trace[(trace[config.lifecycle_col] == 'COMPLETE') | (trace[config.lifecycle_col] == 'complete')].groupby([config.resource_col, config.timestamp_col])

    for (resource, timestamp), group in grouped_complete_events:
        if len(group) > 1:
            concept_names_with_start = []
            # check if any of the grouped events has a start event
            for concept_name in group[config.activity_col]:
                if any((trace[config.activity_col] == concept_name) & 
                        (trace[config.lifecycle_col].str.lower() == 'start') & 
                        (trace[config.timestamp_col] < timestamp)):
                    concept_names_with_start.append(concept_name)
            
            # group events if nessesary
            if (len(group) - len(concept_names_with_start)) > 1 :
                # delete events if they have the same resource and timestamp exept they have a corresponting start event
                trace = trace[~((trace[config.resource_col] == resource) & (trace[config.timestamp_col] == timestamp)) | trace[config.activity_col].isin(concept_names_with_start)]
                # create new aggregate event for all events that have the same resource and timestamp exept they have a start event
                aggregated_name = ' + '.join([name for name in group[config.activity_col].unique() if name not in concept_names_with_start])
                aggregated_event = group.iloc[0].copy()  # Take the first row as base for aggregated event
                aggregated_event[config.activity_col] = aggregated_name
                trace = pd.concat([trace, pd.DataFrame([aggregated_event])], ignore_index=True)
        else:
            continue
    
    return trace.sort_values(by=config.timestamp_col).reset_index(drop=True)  


def add_activity_durations_to_trace(trace: pd.DataFrame) -> pd.DataFrame:
    # trace copy to delete used START events
    trace_copy = trace.copy()
    # trace copy for return
    trace_return = trace.copy()
    # set default activity duration
    trace_return.loc[:, 'duration'] = pd.Timedelta(0)

    for index, row in trace.iterrows():
        if row[config.lifecycle_col] == 'COMPLETE' or row[config.lifecycle_col] == 'complete':
            # For scenario 1: find start event in trace_copy that deletes every used START event
            start_event_copy = trace_copy[(trace_copy[config.activity_col] == row[config.activity_col]) & 
                                    ((trace_copy[config.lifecycle_col] == 'START') | (trace_copy[config.lifecycle_col] == 'start')) & 
                                    (trace_copy[config.timestamp_col] < row[config.timestamp_col])]
            # For scenario 2: find any start event even if it is used before
            start_event = trace_return[(trace_return[config.activity_col] == row[config.activity_col]) & 
                                    ((trace_return[config.lifecycle_col] == 'START') | (trace_return[config.lifecycle_col] == 'start')) & 
                                    (trace_return[config.timestamp_col] < row[config.timestamp_col])]
            
            # scenario 1: Find the FIRST matching START event
            if not start_event_copy.empty:
                # take the first matching START event, that no COMPLETE event has matched before 
                start_time = start_event_copy.iloc[0][config.timestamp_col]
                # Delete the first matching START event from trace_copy, such that no other COMPLETE event can match the START event
                trace_copy.drop(start_event_copy.index[0], inplace=True)
            
            # scenario 2: Find the ANY matching START event
            elif not start_event.empty:
                # take the last matching START event, eaven if some COMPLETE event has already matched
                start_time = start_event.iloc[-1][config.timestamp_col]

            # scenario 3: Use the previous COMPLETE event's timestamp
            else:
                prev_complete_event = trace_return[(trace_return[config.timestamp_col] < row[config.timestamp_col]) & 
                            ((trace_return[config.lifecycle_col] == 'COMPLETE') | (trace_return[config.lifecycle_col] == 'complete'))].tail(1)
                if not prev_complete_event.empty:
                    start_time = prev_complete_event.iloc[0][config.timestamp_col]
                # If it's the first event of the trace, duration is 0
                else:
                    start_time = row[config.timestamp_col]  

            trace_return.at[index, 'duration'] = row[config.timestamp_col] - start_time

    return trace_return

def prepare_trace(trace: pd.DataFrame) -> pd.DataFrame:
    trace_grouped = group_equal_timestamp_events(trace)
    trace_grouped_duration = add_activity_durations_to_trace(trace_grouped)
    trace_grouped_duration_complete = trace_grouped_duration[(trace_grouped_duration[config.lifecycle_col] == 'COMPLETE') | (trace_grouped_duration[config.lifecycle_col] == 'complete')]
    trace_grouped_duration_complete_cleaned = trace_grouped_duration_complete.dropna(subset=[config.resource_col])
    return trace_grouped_duration_complete_cleaned


# get a lower number of ids to reduce case sampling time
def get_n_case_ids(case_ids, n_cases, seed=999):
    np.random.seed(seed)
    if len(case_ids) > n_cases:
        return np.random.choice(case_ids, size=n_cases, replace=False)
    else:
        return case_ids
    
# get a lower number of activities to reduce activity sampling time
def get_n_events(event_log, n_events, seed=999):
    # Filter out rows where config.resource_col is None or NaN
    filtered_event_log = event_log.dropna(subset=[config.resource_col])
    
    if len(filtered_event_log) > n_events:
        # Sample n_events from the filtered DataFrame
        return filtered_event_log.sample(n=n_events, random_state=seed)
    else:
        # If there aren't enough events after filtering, return the filtered DataFrame
        return filtered_event_log