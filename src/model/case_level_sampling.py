import pandas as pd

# E_{T}
def get_events_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> pd.DataFrame:
    return event_log[
        (event_log['time:timestamp'] >= t_start) &
        (event_log['time:timestamp'] < t_end)
    ]

# E_{¬T}
def get_events_not_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> pd.DataFrame:
    return event_log[
        (event_log['time:timestamp'] < t_start) |
        (event_log['time:timestamp'] >= t_end)
    ]

# C_{T} = ids of fully contained cases
def get_caseids_in_time_frame(event_log: pd.DataFrame, t_start: pd.Timestamp, t_end: pd.Timestamp) -> [str]:
    events_in_time_frame = get_events_in_time_frame(event_log, t_start, t_end)
    events_not_in_time_frame = get_events_not_in_time_frame(event_log, t_start, t_end)

    cases_ids_in_time_frame = set(events_in_time_frame['case:concept:name'])
    cases_ids_not_in_time_frame = set(events_not_in_time_frame['case:concept:name'])

    return cases_ids_in_time_frame - cases_ids_not_in_time_frame


def get_trace(event_log: pd.DataFrame, case_id: str) -> pd.DataFrame:
    trace = event_log.loc[event_log['case:concept:name'] == case_id]
    return trace

def group_equal_timestamp_events(trace: pd.DataFrame) -> pd.DataFrame:

    grouped_complete_events = trace[trace['lifecycle:transition'] == 'COMPLETE'].groupby(['org:resource', 'time:timestamp'])

    for (resource, timestamp), group in grouped_complete_events:
        if len(group) > 1:
            concept_names_with_start = []
            for concept_name in group['concept:name'].unique():
                if any((trace['concept:name'] == concept_name) & 
                        (trace['lifecycle:transition'] == 'START') & 
                        (trace['time:timestamp'] < timestamp)):
                    concept_names_with_start.append(concept_name)
            # delete events if they have the same resource and timestamp exept they have a corresponting start event
            trace = trace[~((trace['org:resource'] == resource) & (trace['time:timestamp'] == timestamp)) | trace['concept:name'].isin(concept_names_with_start)]
            # create new grouped event, if nessesary
            if len(concept_names_with_start) < len(group):
                aggregated_name = ' + '.join(list(set(group['concept:name'].unique()) - set(concept_names_with_start)))
                aggregated_event = group.iloc[0]  # Take the first row as base for aggregated event
                aggregated_event['concept:name'] = aggregated_name
                trace = pd.concat([trace, pd.DataFrame([aggregated_event])], ignore_index=True)
        else:
            continue
    
    return trace.sort_values(by='time:timestamp').reset_index(drop=True)  


def add_activity_durations_to_trace(trace: pd.DataFrame) -> pd.DataFrame:

    trace['duration'] = pd.Timedelta(0)

    for index, row in trace.iterrows():
        if row['lifecycle:transition'] == 'COMPLETE':
            # Option 1: Find a matching START event
            start_event = trace[(trace['concept:name'] == row['concept:name']) & 
                                    (trace['lifecycle:transition'] == 'START') & 
                                    (trace['time:timestamp'] < row['time:timestamp'])]
            if not start_event.empty:
                start_time = start_event.iloc[-1]['time:timestamp']

            # Option 2: Use the previous COMPLETE event's timestamp
            else:
                prev_complete_event = trace[(trace['time:timestamp'] < row['time:timestamp']) & 
                            (trace['lifecycle:transition'] == 'COMPLETE')].tail(1)
                if not prev_complete_event.empty:
                    start_time = prev_complete_event.iloc[0]['time:timestamp']
                # If it's the first event of the trace, duration is 0
                else:
                    start_time = row['time:timestamp']  

            trace.at[index, 'duration'] = row['time:timestamp'] - start_time

    return trace

    