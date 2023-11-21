from app import app
from dash import html, Input, Output, dcc, no_update
from datetime import datetime as dt
from model.xes_utility import get_unique_resources, get_earliest_timestamp, get_latest_timestamp, json_to_df


layout = html.Div([
    html.Div(
        className='div-sidebar-options',
        children = [
            html.Div(
                className='div-in-sidebar-options',
                children = [
                    html.Div(
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
                                    {'label': 'Month', 'value': 'month'}
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
                                date=str(dt(2023, 8, 25, 23, 59, 59))
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
                                date=str(dt(2023, 8, 25, 23, 59, 59))
                            ),
                    ]),
                    html.Div(
                        className='div-option-col',
                        children = [

                    ])
                ]
            ),
            
    ])
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
        
        earliest_timestamp = get_earliest_timestamp(df_event_log).replace('Z', '+00:00')
        latest_timestamp = get_latest_timestamp(df_event_log).replace('Z', '+00:00')

        earliest_dt = dt.fromisoformat(earliest_timestamp).date()
        latest_dt = dt.fromisoformat(latest_timestamp).date()

        return [options, earliest_dt, latest_dt, earliest_dt, earliest_dt, earliest_dt, latest_dt, latest_dt, latest_dt]
    else:
        # Return an empty list if no file is selected
        return [no_update] * 9