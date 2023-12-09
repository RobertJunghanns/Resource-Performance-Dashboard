from app import app
import plotly.graph_objs as go
import pandas as pd
from dash import html, State, Input, Output, dcc, no_update
import dash_bootstrap_components as dbc
from model.pickle_utility import load_from_pickle
from model.xes_utility import get_unique_resources, get_earliest_timestamp, get_latest_timestamp, get_period_name, generate_time_period_intervals, generate_until_end_period_intervals
from model.resource_behavior_indicators import sql_to_rbi, rbi_distinct_activities, rbi_activity_fequency, rbi_activity_completions, rbi_case_completions, rbi_fraction_case_completions, rbi_average_workload, rbi_multitasking, rbi_average_duration_activity, rbi_average_case_duration, rbi_interaction_two_resources, rbi_social_position

layout = html.Div([
    dbc.Alert(id='sql-alert', className='alert', duration=40000, color="warning", dismissable=True, is_open=False),
    html.Div(
        id='page-resource',
        children = [
        html.Div(
            className='div-sidebar-options',
            children = [
                html.Div(
                    className='div-div-sidebar-options',
                    children = [
                        html.Div(
                            className='div-div-div-sidebar-options',
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
                                                {'label': 'Case completions', 'value': 'rbi_case_completions'},
                                                {'label': 'Fraction case completion', 'value': 'rbi_fraction_case_completion'},
                                                {'label': 'Average workload', 'value': 'rbi_average_workload'},
                                                {'label': 'Mulitasking', 'value': 'rbi_multitasking'},
                                                {'label': 'Average duration activity', 'value': 'rbi_average_duration_activity'},
                                                {'label': 'Average case duration', 'value': 'rbi_average_duration_case'},
                                                {'label': 'Interaction two resources', 'value': 'rbi_interaction_two_resources'},
                                                {'label': 'Social position', 'value': 'rbi_social_position'},
                                            ]
                                        ),
                                        html.Div(id='dynamic-additional-input-fields', children=[
                                            html.Div([
                                                html.P('SQL query:', className='p-option-col'),
                                                dcc.Textarea(
                                                    id='input-sql-query',
                                                    placeholder="Enter SQL query. Example for activity frequency:\nSELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)\n   FROM (\n      SELECT\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = 'resource_id'\n         AND [concept:name] = '09_AH_I_010')\n         AS activity,\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = 'resource_id')\n         AS all_activities\n   ) AS count",
                                                ),
                                            ], id='sql-input-container', style={'display': 'none'}),
                                            html.Div([
                                                html.P('Activity name:', className='p-option-col'),
                                                dcc.Input(id='input-concept-name', type='text', placeholder=' Enter concept:name...'),
                                            ], id='concept-name-input-container', style={'display': 'none'}), 
                                            html.Div([
                                                html.P('Interaction resource id:', className='p-option-col'),
                                                dcc.Input(id='input-resource-name', type='text', placeholder=' Enter org:resource...'),
                                            ], id='resource-id-input-container', style={'display': 'none'}),
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
    Input('pickle_df_name', 'data')
)
def update_resource_options(pickle_df_name):
    if pickle_df_name:
        df_event_log = load_from_pickle(pickle_df_name)
        unique_resources = get_unique_resources(df_event_log)
        sorted_resources = sorted(unique_resources)
        options = [{'label': resource, 'value': str(resource)} for resource in sorted_resources]
        
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
    [State('pickle_df_name', 'data'),
     State('dropdown-rbi-select', 'value'),
     State('dropdown-resource-select', 'value'),
     State('date-from', 'date'), 
     State('date-to', 'date'),
     State('dropdown-time-select', 'value'),
     State('dropdown-scope-select', 'value'),
     State('input-sql-query', 'value'),
     State('input-concept-name', 'value'),
     State('input-resource-name', 'value')]
)
def get_rbi_time_series(n_clicks, pickle_df_name, rbi, resource, start_date_str, end_date_str, period, scope, sql_query, concept_name, interaction_resource):
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
    
    df_event_log = load_from_pickle(pickle_df_name)
    
    if all(variable is not None and variable for variable in [rbi, resource, start_date_str, end_date_str, period, scope]):
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

        rbi_time_series_names = []
        rbi_time_series_values = []
        for interval in time_intervals:
            if scope=='in_period':
                rbi_time_series_names.append(get_period_name(interval[0], period))
            elif scope == 'until_period':
                rbi_time_series_names.append(get_period_name(interval[2], period))

            if rbi == 'rbi_sql':
                try:
                    rbi_time_series_values.append(sql_to_rbi(df_event_log, sql_query, resource, interval[0], interval[1]))
                except Exception as error:
                    return no_figure, 'SQL failed:\n' + str(error), True  
            elif rbi == 'rbi_distinct_activities':
                rbi_time_series_values.append(rbi_distinct_activities(df_event_log, interval[0], interval[1], resource))
            elif rbi == 'rbi_activity_frequency':
                rbi_time_series_values.append(rbi_activity_fequency(df_event_log, interval[0], interval[1], resource, concept_name))
            elif rbi == 'rbi_activity_completions':
                rbi_time_series_values.append(rbi_activity_completions(df_event_log, interval[0], interval[1], resource))
            elif rbi == 'rbi_case_completions':
                rbi_time_series_values.append(rbi_case_completions(df_event_log, interval[0], interval[1], resource))
            elif rbi == 'rbi_fraction_case_completion':
                rbi_time_series_values.append(rbi_fraction_case_completions(df_event_log, interval[0], interval[1], resource))
            elif rbi == 'rbi_average_workload':
                rbi_time_series_values.append(rbi_average_workload(df_event_log, interval[0], interval[1], resource))
            elif rbi == 'rbi_multitasking':
                rbi_time_series_values.append(rbi_multitasking(df_event_log, interval[0], interval[1], resource))
            elif rbi == 'rbi_average_duration_activity':
                rbi_time_series_values.append(rbi_average_duration_activity(df_event_log, interval[0], interval[1], resource, concept_name))
            elif rbi == 'rbi_average_duration_case':
                rbi_time_series_values.append(rbi_average_case_duration(df_event_log, interval[0], interval[1], resource))
            elif rbi == 'rbi_interaction_two_resources':
                rbi_time_series_values.append(rbi_interaction_two_resources(df_event_log, interval[0], interval[1], resource, interaction_resource))
            elif rbi == 'rbi_social_position':
                rbi_time_series_values.append(rbi_social_position(df_event_log, interval[0], interval[1], resource))
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
     Output('resource-id-input-container', 'style')],
    Input('dropdown-rbi-select', 'value')
)
def toggle_input_fields_visibility(selected_rbi):
    inputs_visibility = [{'display': 'none'}] * 3 # set to number of input containers

    if selected_rbi == 'rbi_sql':
        inputs_visibility[0] = {'display': 'block'} 
    elif selected_rbi == 'rbi_activity_frequency' or selected_rbi =='rbi_average_duration_activity':
        inputs_visibility[1] = {'display': 'block'}
    elif selected_rbi == 'rbi_interaction_two_resources':
        inputs_visibility[2] = {'display': 'block'}

    return inputs_visibility