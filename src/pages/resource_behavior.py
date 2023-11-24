from app import app
import plotly.graph_objs as go
import pandas as pd
from dash import html, State, Input, Output, dcc, no_update
import dash_bootstrap_components as dbc
from model.xes_utility import get_unique_resources, get_earliest_timestamp, get_latest_timestamp, get_period_name, generate_time_period_intervals, generate_until_end_period_intervals, json_to_df, df_to_json
from model.resource_behavior_indicators import sql_to_rbi, rbi_distinct_activities, rbi_activity_fequency, rbi_activity_completions

layout = html.Div([
    dbc.Alert(id='sql-alert', className='alert', duration=40000, color="warning", dismissable=True, is_open=False),
    html.Div(
        id='page-resource',
        children = [
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
                                        children='Resource:', 
                                    ),
                                    dcc.Dropdown(
                                        id='dropdown-resource-select',
                                        options=[]
                                    ),
                                    html.P(
                                        className='p-option-col',
                                        children='Time period:', 
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
                                        children='Backwards scope:', 
                                    ),
                                    dcc.Dropdown(
                                        id='dropdown-scope-select',
                                        options=[
                                            {'label': 'ONLY time period', 'value': 'in_period'},
                                            {'label': 'UNTIL end of time period', 'value': 'until_period'},
                                        ],
                                        value='in_period'
                                    ),
                                    html.P(
                                        className='p-option-col',
                                        children='Date from:', 
                                    ),
                                    dcc.DatePickerSingle(
                                        id='date-from',
                                        className='date-select',
                                        min_date_allowed=pd.Timestamp('1995-08-05'),
                                        max_date_allowed=pd.Timestamp('2023-11-30'),
                                        initial_visible_month=pd.Timestamp('2023-11-30'),
                                        date=pd.Timestamp('2023-11-30')
                                    ),
                                    html.P(
                                        className='p-option-col',
                                        children='Date up to:', 
                                    ),
                                    dcc.DatePickerSingle(
                                        id='date-to',
                                        className='date-select',
                                        min_date_allowed=pd.Timestamp('1995-08-05'),
                                        max_date_allowed=pd.Timestamp('2023-11-30'),
                                        initial_visible_month=pd.Timestamp('2023-11-30'),
                                        date=pd.Timestamp('2023-11-30')
                                    ),
                                ]),
                                html.Div(
                                    id='div-option-col-right',
                                    className='div-option-col',
                                    children = [
                                        html.P(
                                            className='p-option-col',
                                            children='Resource behavior indicator:', 
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown-rbi-select',
                                            options=[
                                                {'label': 'Custom RBI (SQL)', 'value': 'rbi_sql'},
                                                {'label': 'Distinct activities', 'value': 'rbi_distinct_activities'},
                                                {'label': 'Activity frequency', 'value': 'rbi_activity_frequency'},
                                                {'label': 'Activity completions', 'value': 'rbi_activity_completions'},
                                            ],
                                            value='month'
                                        ),
                                        html.Div(id='dynamic-additional-input-fields', children=[
                                            html.Div([
                                                html.P('SQL query:', className='p-option-col'),
                                                dcc.Textarea(
                                                    id='input-sql-query',
                                                    placeholder="Enter SQL query. Example for activity frequency:\nSELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)\n   FROM (\n      SELECT\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = 'resource_id'\n         AND [concept:name] = '09_AH_I_010')\n         AS activity,\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = 'resource_id')\n         AS all_activities\n   ) AS count",
                                                ),
                                            ], id='sql-input-container', style={'display': 'none'}),  # Initially hidden
                                            html.Div([
                                                html.P('Activity name:', className='p-option-col'),
                                                dcc.Input(id='input-concept-name', type='text', placeholder=' Enter concept:name...'),
                                            ], id='concept-name-input-container', style={'display': 'none'}),  # Initially hidden

                                            # Add more input field containers here and set their display to 'none'
                                            # ...

                                        ]),
                                ]),
                        ]),
                        html.Button(
                            'Generate Time Series Diagram',
                            id='button-generate',
                        )   
                    ]),
            ]),
            dcc.Loading(
                id="loading-chart",
                children=[dcc.Graph(id='time-series-chart')],
                type="circle", 
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
        
        earliest_dt = get_earliest_timestamp(df_event_log)
        latest_dt = get_latest_timestamp(df_event_log)

        return [options, earliest_dt, latest_dt, earliest_dt, earliest_dt, earliest_dt, latest_dt, latest_dt, latest_dt]
    else:
        # Return an empty list if no file is selected
        return [no_update] * 9

@app.callback(
    Output('time-series-chart', 'figure'),
    Output('sql-alert', 'children'),
    Output('sql-alert', 'is_open'),
    Input('button-generate', 'n_clicks'),
    [State('json_event_log', 'data'),
     State('dropdown-rbi-select', 'value'),
     State('dropdown-resource-select', 'value'),
     State('date-from', 'date'), 
     State('date-to', 'date'),
     State('dropdown-time-select', 'value'),
     State('dropdown-scope-select', 'value'),
     State('input-sql-query', 'value'),
     State('input-concept-name', 'value')]
)
def get_rbi_time_series(n_clicks, event_log_json, rbi, resource, start_date_str, end_date_str, period, scope, sql_query, concept_name):
    no_figure = go.Figure(layout={
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'Select options and press "Generate Time Series Diagram".',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {
                        'size': 16
                    }
                }]
            })
    
    if all(variable is not None and variable for variable in [event_log_json, rbi, resource, start_date_str, end_date_str, period, scope]):
        # convert date strings
        start_date = pd.to_datetime(start_date_str)
        end_date = pd.to_datetime(end_date_str)

        if start_date.tzinfo is None:
            start_date = start_date.tz_localize('UTC')
        if end_date.tzinfo is None:
            end_date = end_date.tz_localize('UTC')
        # generate intervals
        if scope == 'in_period': 
            time_intervals = generate_time_period_intervals(start_date, end_date, period)
        elif scope == 'until_period':
            time_intervals = generate_until_end_period_intervals(start_date, end_date, period)

        event_log_df = json_to_df(event_log_json)
        rbi_time_series_names = []
        rbi_time_series_values = []
        for interval in time_intervals:
            if scope=='in_period':
                rbi_time_series_names.append(get_period_name(interval[0], period))
            elif scope == 'until_period':
                rbi_time_series_names.append(get_period_name(interval[2], period))


            if rbi == 'rbi_sql':
                try:
                    rbi_time_series_values.append(sql_to_rbi(sql_query, event_log_df, interval[0], interval[1], resource))
                except Exception as error:
                    return no_figure, 'SQL failed:\n' + str(error), True  
            elif rbi == 'rbi_distinct_activities':
                rbi_time_series_values.append(rbi_distinct_activities(event_log_df, interval[0], interval[1], resource))
            elif rbi == 'rbi_activity_frequency':
                rbi_time_series_values.append(rbi_activity_fequency(event_log_df, interval[0], interval[1], resource, concept_name))
            elif rbi == 'rbi_activity_completions':
                rbi_time_series_values.append(rbi_activity_completions(event_log_df, interval[0], interval[1], resource))
            else:
                return no_figure, no_update, no_update
            
        fig = go.Figure([go.Scatter(x=rbi_time_series_names, y=rbi_time_series_values)])

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="RBI Value",
            title="RBI Time Series"
        )
                
        return fig, no_update, no_update
    
    return no_figure, no_update, no_update
    
# toggle the visibility of input fields
@app.callback(
    [Output('sql-input-container', 'style'),
     Output('concept-name-input-container', 'style'),
     # Add more Outputs for other input containers here
    ],
    Input('dropdown-rbi-select', 'value')
)
def toggle_input_fields_visibility(selected_rbi):
    inputs_visibility = [{'display': 'none'}] * 2 # set to number of input containers

    if selected_rbi == 'rbi_sql':
        inputs_visibility[0] = {'display': 'block'} 
    elif selected_rbi == 'rbi_activity_frequency':
        inputs_visibility[1] = {'display': 'block'}

    return inputs_visibility