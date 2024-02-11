import datetime as dt
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from app import app
from dash import html, State, Input, Output, dcc, no_update

from framework.utility.pickle_utility import load_from_pickle
from framework.utility.xes_utility import get_unique_resources, get_earliest_timestamp, get_latest_timestamp
from framework.sampling.time_series_sampling import get_period_name, generate_time_period_intervals, generate_until_end_period_intervals
from framework.measures.resource_behavior_indicators import sql_to_rbi, rbi_distinct_activities, rbi_activity_fequency, rbi_activity_completions, rbi_case_completions, rbi_fraction_case_completions, rbi_average_workload, rbi_multitasking, rbi_average_duration_activity, rbi_interaction_two_resources, rbi_social_position

layout = html.Div([
    dbc.Alert(id='input-alert', className='margin-top', duration=40000, color="warning", dismissable=True, is_open=False),
    html.Div(
        className='flex-row width-100',
        children = [
        html.Div(
            className='div-sidebar',
            children = [
                html.Div(
                    className='div-div-sidebar flex-row',
                    children = [
                        html.Div(
                            className="margin-top",
                            children=html.Img(
                                className='img-input',
                                src=("./assets/images/resource.png"),
                            ), 
                        ),
                        html.Div(
                            className='margin-left width-100 flex-col',
                            children = [
                                html.P(
                                    className='p-option-col',
                                    children=[
                                        'Resource ID ',
                                        html.Span('*', style={'color': 'red'})
                                    ]
                                ),
                                dcc.Dropdown(
                                    id='dropdown-resource-select',
                                    className='',
                                    options=[]
                                )
                        ]),
                ]),
                html.Div(
                    className='div-div-sidebar flex-row',
                    children = [
                        html.Div(
                            className="margin-top",
                            children=html.Img(
                                id='img-rbi',
                                src=("./assets/images/rbi.png"),
                            ), 
                        ),
                        html.Div(
                            className='margin-left width-100 flex-col',
                            children = [
                                html.P(
                                    className='p-option-col',
                                    children=[
                                        'Resource behavior indicator ',
                                        html.Span('*', style={'color': 'red'})
                                    ]
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
                                        {'label': 'Interaction two resources', 'value': 'rbi_interaction_two_resources'},
                                        {'label': 'Social position', 'value': 'rbi_social_position'},
                                    ]
                                ),
                                html.Div(id='dynamic-additional-input-fields', children=[
                                    html.Div([
                                        html.P('SQL query:', className='p-option-col'),
                                        dcc.Textarea(
                                            id='input-sql-query',
                                            className='input sql-input hight-235',
                                            placeholder="Enter SQL query. Example for activity frequency:\nSELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)\n   FROM (\n      SELECT\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = '{r}'\n         AND [concept:name] = '09_AH_I_010')\n         AS activity,\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = '{r}')\n         AS all_activities\n   ) AS count",
                                        ),
                                    ], id='sql-input-container', style={'display': 'none'}),
                                    html.Div([
                                        html.P('Activity name:', className='p-option-col'),
                                        dcc.Input(id='input-concept-name', className='input hight-35', type='text', placeholder=' Enter concept:name...'),
                                    ], id='concept-name-input-container', style={'display': 'none'}), 
                                    html.Div([
                                        html.P('Interaction resource id:', className='p-option-col'),
                                        dcc.Input(id='input-resource-name', className='input hight-35', type='text', placeholder=' Enter org:resource...'),
                                    ], id='resource-id-input-container', style={'display': 'none'}),
                                ]),
                        ]),
                ]),
                html.Div(
                    className='div-div-sidebar flex-row',
                    children = [
                        html.Div(
                            className="margin-top",
                            children=html.Img(
                                className='img-input',
                                src=("./assets/images/calendar.png"),
                            ), 
                        ),
                        html.Div(
                            className='flex-col',
                            children=[
                                html.Div(
                                    className='margin-left flex-row',
                                    children=[
                                        html.Div([
                                            html.P(
                                                className='p-option-col',
                                                children=[
                                                    'Time from ',
                                                    html.Span('*', style={'color': 'red'})
                                                ]
                                            ),
                                            dcc.DatePickerSingle(
                                                id='date-from',
                                                className='date-select',
                                                min_date_allowed=pd.Timestamp('1995-08-05'),
                                                max_date_allowed=pd.Timestamp('2023-11-30'),
                                                initial_visible_month=pd.Timestamp('2023-11-30'),
                                                date=pd.Timestamp('2023-11-30')
                                            ),
                                            dmc.TimeInput(
                                                id='time-from',
                                                className='margin-top-5',
                                                format="24",
                                                withSeconds=True,
                                                value=dt.datetime.combine(dt.date.today(), dt.time.min)
                                            ),
                                        ]),
                                        html.Div(
                                            id='div-second-date',
                                            children=[
                                                html.P(
                                                    className='p-option-col',
                                                    children=[
                                                        'Time to ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ]
                                                ),
                                                dcc.DatePickerSingle(
                                                    id='date-to',
                                                    className='date-select',
                                                    min_date_allowed=pd.Timestamp('1995-08-05'),
                                                    max_date_allowed=pd.Timestamp('2023-11-30'),
                                                    initial_visible_month=pd.Timestamp('2023-11-30'),
                                                    date=pd.Timestamp('2023-11-30')
                                                ),
                                                dmc.TimeInput(
                                                    id='time-to',
                                                    className='margin-top-5',
                                                    format="24",
                                                    withSeconds=True,
                                                    value=dt.datetime.combine(dt.date.today(), dt.time.min)
                                                ),
                                        ]),
                                ]),
                                html.Div(
                                    className='margin-left',
                                    children=[
                                        html.P(
                                            className='p-option-col',
                                            children=[
                                                'Time period ',
                                                html.Span('*', style={'color': 'red'})
                                            ]
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
                                            children=[
                                                'Backwards scope ',
                                                html.Span('*', style={'color': 'red'})
                                            ]
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown-scope-select',
                                            options=[
                                                {'label': 'Start of time period', 'value': 'start_period'},
                                                {'label': 'Start of event log', 'value': 'start_log'},
                                            ],
                                            value='start_period'
                                        ), 
                                ])
                            ]
                        ),
                        html.Div(
                            className='div-center-button',
                            children=[
                                html.Button(
                                    'Generate Time Series Diagram',
                                    id='button-generate',
                                    className='button-generate',
                                ),
                            ]
                        )
                ])
            ]),
            dcc.Loading(
                id="loading-chart",
                children=[dcc.Graph(id='time-series-chart')],
                type="circle", 
            ),
    ])
])

# Initialize possible options dependent on XES file
@app.callback(
    [Output('dropdown-resource-select', 'options'),
     Output('date-from', 'min_date_allowed'),
     Output('date-from', 'max_date_allowed'),
     Output('date-from', 'initial_visible_month'),
     Output('date-from', 'date'),
     Output('time-from', 'value'),
     Output('date-to', 'min_date_allowed'),
     Output('date-to', 'max_date_allowed'),
     Output('date-to', 'initial_visible_month'),
     Output('date-to', 'date'),],
     Output('time-to', 'value'),
    Input('pickle_df_name', 'data')
)
def update_resource_options(pickle_df_name):
    if pickle_df_name:
        df_event_log = load_from_pickle(pickle_df_name)
        unique_resources = get_unique_resources(df_event_log)
        sorted_resources = sorted(unique_resources)
        options = [{'label': resource, 'value': str(resource)} for resource in sorted_resources]
        
        earliest_timestamp = get_earliest_timestamp(df_event_log)
        latest_timestamp = get_latest_timestamp(df_event_log)

        earliest_date = earliest_timestamp.date()
        latest_date = latest_timestamp.date()

        earliest_time = earliest_timestamp.time()
        latest_time = latest_timestamp.time()

        earliest_datetime = dt.datetime.combine(earliest_date, earliest_time)
        latest_datetime = dt.datetime.combine(latest_date, latest_time)

        return [options, earliest_date, latest_date, earliest_date, earliest_date, earliest_datetime, earliest_date, latest_date, latest_date, latest_date, latest_datetime]
    else:
        # Return an empty list if no file is selected
        return [no_update] * 11

# sample and display time series
@app.callback(
    Output('time-series-chart', 'figure'),
    Output('input-alert', 'children'),
    Output('input-alert', 'is_open'),
    Input('button-generate', 'n_clicks'),
    [State('pickle_df_name', 'data'),
     State('dropdown-rbi-select', 'value'),
     State('dropdown-resource-select', 'value'),
     State('date-from', 'date'),
     State('time-from', 'value'),
     State('date-to', 'date'),
     State('time-to', 'value'),
     State('dropdown-time-select', 'value'),
     State('dropdown-scope-select', 'value'),
     State('input-sql-query', 'value'),
     State('input-concept-name', 'value'),
     State('input-resource-name', 'value')]
)
def get_rbi_time_series(n_clicks, pickle_df_name, rbi, resource, date_from_str, time_from_str, date_to_str, time_to_str, period, scope, sql_query, concept_name, interaction_resource):
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
    
    if n_clicks is None:
        return no_figure, no_update, no_update
    
    if pickle_df_name is None:
        return no_figure, 'Select XES file before generating!', True
    
    df_event_log = load_from_pickle(pickle_df_name)
    
    # check for None values
    if all(variable is not None and variable for variable in [rbi, resource, date_from_str, time_from_str, date_to_str, time_to_str, period, scope]):
        # convert timestamp strings
        timestamp_from_str = date_from_str + 'T' + time_from_str.split('T')[1] + '+00:00'
        timestamp_to_str = date_to_str + 'T' + time_to_str.split('T')[1] + '+00:00'

        timestamp_from = pd.Timestamp(timestamp_from_str)
        timestamp_to = pd.Timestamp(timestamp_to_str)

        # generate intervals
        if scope == 'start_period': 
            time_intervals = generate_time_period_intervals(timestamp_from, timestamp_to, period)
        elif scope == 'start_log':
            time_intervals = generate_until_end_period_intervals(timestamp_from, timestamp_to, period)

        rbi_time_series_names = []
        rbi_time_series_values = []
        for interval in time_intervals:
            if scope=='start_period':
                rbi_time_series_names.append(get_period_name(interval[0], period))
            elif scope == 'start_log':
                rbi_time_series_names.append(get_period_name(interval[2], period))

            if rbi == 'rbi_sql':
                try:
                    rbi_time_series_values.append(sql_to_rbi(df_event_log, interval[0], interval[1], resource, sql_query))
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
            elif rbi == 'rbi_interaction_two_resources':
                rbi_time_series_values.append(rbi_interaction_two_resources(df_event_log, interval[0], interval[1], resource, interaction_resource))
            elif rbi == 'rbi_social_position':
                rbi_time_series_values.append(rbi_social_position(df_event_log, interval[0], interval[1], resource))
            else:
                return no_figure, no_update, no_update
            
        rbi_function_mapping = {
            'rbi_sql': 'Custom RBI (SQL)',
            'rbi_distinct_activities': 'Distinct activities',
            'rbi_activity_frequency': 'Activity frequency',
            'rbi_activity_completions': 'Activity completions',
            'rbi_case_completions': 'Case completions',
            'rbi_fraction_case_completion': 'Fraction case completion',
            'rbi_average_workload': 'Average workload',
            'rbi_multitasking': 'Multitasking',
            'rbi_average_duration_activity': 'Average duration activity',
            'rbi_interaction_two_resources': 'Interaction two resources',
            'rbi_social_position': 'Social position'
        }

        # Retrieve only the label for a given independent_variable_value
        rbi_label = rbi_function_mapping.get(rbi, '')
            
        fig = go.Figure([go.Scatter(x=rbi_time_series_names, y=rbi_time_series_values)])

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title=rbi_label,
            title="RBI Time Series"
        )
                
        return fig, no_update, no_update
    else:
        return no_figure, 'Fill out all required fields (*) before generating!', True
    
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