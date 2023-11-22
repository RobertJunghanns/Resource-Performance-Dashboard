from app import app
import pm4py
from dash import html, State, Input, Output, dcc, no_update
from datetime import datetime as dt
from model.xes_utility import get_unique_resources, get_earliest_timestamp, get_latest_timestamp, generate_full_time_intervals, json_to_df, df_to_json


layout = html.Div([
    html.Div(
        className='div-sidebar-options',
        children = [
            html.Div(
                id='div-div-sidebar-options',
                children = [
                    html.Div(
                        id='div-div-div-sidebar-options',
                        children = [
                            html.Div(
                            id='div-option-col-left',
                            className='div-option-col',
                            children = [
                                html.P(
                                    className='p-option-col',
                                    children='Resource', 
                                ),
                                dcc.Dropdown(
                                    id='dropdown-resource-select',
                                    options=[]
                                ),
                                html.P(
                                    className='p-option-col',
                                    children='Time period', 
                                ),
                                dcc.Dropdown(
                                    id='dropdown-time-select',
                                    options=[
                                        {'label': 'Day', 'value': 'day'},
                                        {'label': 'Week', 'value': 'week'},
                                        {'label': 'Month', 'value': 'month'},
                                        {'label': 'Year', 'value': 'year'}
                                    ],
                                    value='month'
                                ),
                                html.P(
                                    className='p-option-col',
                                    children='Date from', 
                                ),
                                dcc.DatePickerSingle(
                                    id='date-from',
                                    className='date-select',
                                    min_date_allowed=dt(1995, 8, 5),
                                    max_date_allowed=dt(2023, 9, 19),
                                    initial_visible_month=dt(2023, 8, 5),
                                    date=dt(2023, 8, 25, 23, 59, 59)
                                ),
                                html.P(
                                    className='p-option-col',
                                    children='Date up to', 
                                ),
                                dcc.DatePickerSingle(
                                    id='date-to',
                                    className='date-select',
                                    min_date_allowed=dt(1995, 8, 5),
                                    max_date_allowed=dt(2023, 9, 19),
                                    initial_visible_month=dt(2023, 8, 5),
                                    date=dt(2023, 8, 25, 23, 59, 59)
                                ),
                            ]),
                            html.Div(
                                id='div-option-col-right',
                                className='div-option-col',
                                children = [
                                    html.P(
                                        className='p-option-col',
                                        children='Resource Behavior Indicators', 
                                    ),
                                dcc.Checklist(
                                        id='checklist-rbi',
                                        className='checklist-button-box',
                                        options=[
                                            {'label': 'Option 1', 'value': 'OPT1'},
                                            {'label': 'Option 2', 'value': 'OPT2'},
                                            {'label': 'Option 3', 'value': 'OPT3'},
                                        ],
                                        value=[],
                                        inputStyle={"margin-right": "5px"},
                                        labelStyle={"display": "inline"}
                                    ),  
                            ]),
                    ]),
                    html.Button(
                        'Generate Time Series Diagrams',
                        id='button-generate',
                    )  
                    
            ]),
    ]),
    html.Div(id='placeholder')
])

@app.callback(
    [Output('dropdown-resource-select', 'options'),
     Output('date-from', 'min_date_allowed'),
     Output('date-from', 'max_date_allowed'),
     Output('date-from', 'initial_visible_month'),
     Output('date-from', 'date'),
     Output('date-to', 'min_date_allowed'),
     Output('date-to', 'max_date_allowed'),
     Output('date-to', 'initial_visible_month'),
     Output('date-to', 'date'),],
    Input('json_event_log', 'data')
)
def update_resource_options(json_event_log):
    if json_event_log:
        df_event_log = json_to_df(json_event_log)
        unique_resources = get_unique_resources(df_event_log)
        sorted_resources = sorted(unique_resources)
        options = [{'label': resource, 'value': resource} for resource in sorted_resources]
        
        earliest_dt = get_earliest_timestamp(df_event_log)
        latest_dt = get_latest_timestamp(df_event_log)

        return [options, earliest_dt, latest_dt, earliest_dt, earliest_dt, earliest_dt, latest_dt, latest_dt, latest_dt]
    else:
        # Return an empty list if no file is selected
        return [no_update] * 9
    
# @app.callback(
#     Output('json_filtered_event_log', 'data'),
#     [Input('date-from', 'date'), 
#      Input('date-to', 'date')],
#     [State('json_event_log', 'data')]
# )
# def filter_event_log(start_date_str, end_date_str, event_log_json):
#      # Convert datetime strings to the string format expected by PM4Py
#     start_date = dt.fromisoformat(start_date_str)
#     end_date = dt.fromisoformat(end_date_str)
#     start_date_formatted = start_date.strftime("%Y-%m-%d %H:%M:%S")
#     end_date_formatted = end_date.strftime("%Y-%m-%d %H:%M:%S")

#     event_log_df = json_to_df(event_log_json)
#     filtered_log = pm4py.filter_time_range(event_log_df, start_date_formatted, end_date_formatted, mode='traces_contained')
#     filtered_event_log_json = df_to_json(filtered_log)
    
#     return filtered_event_log_json

@app.callback(
    Output('placeholder', 'children'),
    [Input('date-from', 'date'), 
     Input('date-to', 'date'),
     Input('dropdown-time-select', 'value')]
)
def filter_event_log(start_date_str, end_date_str, period):
    time_intervals = generate_full_time_intervals(start_date_str, end_date_str, period)
    #print(time_intervals)
    return None