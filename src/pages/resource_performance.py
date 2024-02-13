import pandas as pd
import uuid
import json
import datetime as dt

from app import app
from dash import html, Input, Output, State, dcc, no_update, ALL, callback_context
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px

from framework.utility.pickle_utility import load_from_pickle
from framework.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp, get_column_names, count_unique_cases, count_completed_events
from framework.sampling.case_level_sampling import ScopeCase, sample_regression_data_case
from framework.sampling.activity_level_sampling import ScopeActivity, sample_regression_data_activity
from framework.measures.resource_behavior_indicators import sql_to_rbi, rbi_distinct_activities, rbi_activity_fequency, rbi_activity_completions, rbi_case_completions, rbi_fraction_case_completions, rbi_average_workload, rbi_multitasking, rbi_average_duration_activity, rbi_interaction_two_resources, rbi_social_position
from framework.measures.case_performance_measures import sql_to_case_performance_metric, case_duration
from framework.measures.activity_performance_measures import activity_duration
from framework.regression_analysis import fit_regression

panel_id=0

# Define the page layout
layout = html.Div([
    dbc.Alert(id='input-alert-rp', className='margin-top', duration=40000, color="warning", dismissable=True, is_open=False),
    html.Div(
        className='flex-row',
        id='page-resource-performance',
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
                                id='img-sample',
                                src=("./assets/images/sample.png"),
                            ), 
                        ),
                        html.Div(
                            className='margin-left width-100',
                            children = [
                                html.P(
                                    className='p-option-col',
                                    children=[
                                        'Sampling Strategy ',
                                        html.Span('*', style={'color': 'red'})
                                    ]
                                ),
                                dcc.Dropdown(
                                    id='dropdown-sampling-strategy',
                                    options=[
                                        {'label': 'Case level sampling', 'value': 'case_level'},
                                        {'label': 'Activity level sampling', 'value': 'activity_level'},
                                    ],
                                    value='case_level'
                                ),
                                html.Div(
                                    className='flex-row width-100',
                                    children = [
                                         html.Div(
                                            [
                                                html.P(
                                                    className='p-option-col',
                                                    children='Filter attribute'
                                                ),
                                                dcc.Dropdown(
                                                    id='dropdown-filter-attribute-select',
                                                    className = 'width-100',
                                                    options=[]
                                                ),
                                            ],
                                            style={'display': 'none'},
                                            className='margin-right width-60',
                                            id='div-filter-attribute-select'
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    className='p-option-col',
                                                    children='Attribute value'
                                                ),
                                                dcc.Input(id='filter-attribute-value', className='input hight-35', placeholder=' Attribute value')
                                            ],
                                            style={'display': 'none'},
                                            className='width-40',
                                            id='div-filter-attribute-value'
                                        ),
                                ]),
                                html.Div(
                                    className='flex-row',
                                    children = [
                                        html.Div(
                                            [
                                                html.P(
                                                    className='p-option-col',
                                                    children=[
                                                        'Max. number of cases ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ]
                                                ),
                                                dcc.Input(id='case-num-limit', className='input hight-35', type='number', placeholder=' Maximum number of cases')
                                            ],
                                            style={'display': 'none'},
                                            className='margin-right width-60',
                                            id='div-max-cases'
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    className='p-option-col',
                                                    children=[
                                                        'Max. number of activities ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ]
                                                ),
                                                dcc.Input(id='activity-num-limit', className='input hight-35', type='number', placeholder=' Maximum number of activities')
                                            ],
                                            style={'display': 'none'},
                                            className='margin-right width-60',
                                            id='div-max-activities'
                                        ),
                                        html.Div(
                                            [
                                                html.P(
                                                    className='p-option-col',
                                                    children=[
                                                        'Seed ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ]
                                                ),
                                                dcc.Input(id='sampling-seed', className='input hight-35', type='number', value=999)
                                            ],
                                            className='width-40',
                                            id='div-seed'
                                        )
                                ])
                        ])
                ]),
                html.Div(
                    id='select-relationship-container',
                    className='div-div-sidebar flex-col',
                    children = [
                        html.Div(
                            className='flex-row width-100',
                            children=[
                                html.Div(
                                    className="margin-top",
                                    children=html.Img(
                                        id='img-rbi',
                                        src=("./assets/images/rbi.png"),
                                    ), 
                                ),
                                html.Div(
                                    className='margin-left width-100',
                                    children=[
                                        html.P(
                                            className='p-option-col',
                                            children=[
                                                'Independent Variable (RBI) ',
                                                html.Span('*', style={'color': 'red'})
                                            ]
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown-iv-select',
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
                                        html.Div([
                                            html.Div([
                                                html.P(
                                                    children=[
                                                        'SQL query ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ],
                                                    className='p-option-col'
                                                ),
                                                dcc.Textarea(
                                                    id='input-iv-sql-query-rp',
                                                    className='input sql-input hight-235',
                                                    placeholder="Enter SQL query. Example for activity frequency:\nSELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)\n   FROM (\n      SELECT\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = '{r}'\n         AND [concept:name] = '09_AH_I_010')\n         AS activity,\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = '{r}')\n         AS all_activities\n   ) AS count",
                                                ),
                                            ], id='sql-input-iv-container-rp', style={'display': 'none'}),
                                            html.Div([
                                                html.P(
                                                    children=[
                                                        'Max. number of cases ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ],
                                                    className='p-option-col'
                                                ),
                                                dcc.Input(id='input-concept-name-rp', className='input hight-35', type='text', placeholder=' Enter concept:name...'),
                                            ], id='concept-name-input-container-rp', style={'display': 'none'}), 
                                            html.Div([
                                                html.P(
                                                    children=[
                                                        'Interaction resource id ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ],
                                                    className='p-option-col'
                                                ),
                                                dcc.Input(id='input-resource-name-rp', className='input hight-35', type='text', placeholder=' Enter org:resource...'),
                                            ], id='resource-id-input-container-rp', style={'display': 'none'}),
                                        ]),
                                ])
                            ]
                        ),
                        html.Div(
                            id='select-arrow',
                            children=[
                                html.Div(
                                    children=html.Img(
                                        id='img-down-arrow',
                                        src=("./assets/images/down-arrow.png"),
                                    ),
                                ),
                            ]
                        ),
                        html.Div(
                            id='select-performance-dv',
                            className='flex-row',
                            children=[
                                html.Div(
                                    className="margin-top",
                                    children=html.Img(
                                        className='img-input',
                                        src=("./assets/images/performance.png"),
                                    ), 
                                ),
                                html.Div(
                                    className='margin-left width-100',
                                    children=[
                                        html.P(
                                            className='p-option-col',
                                            children=[
                                                'Dependent Variable (Performance Metric) ',
                                                html.Span('*', style={'color': 'red'})
                                            ]
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown-dv-select',
                                            options=[]
                                        ),
                                        html.Div([
                                            html.Div([
                                                html.P('SQL query:', className='p-option-col'),
                                                dcc.Textarea(
                                                    id='input-dv-sql-query-rp',
                                                    className='input sql-input hight-100',
                                                    placeholder="Enter SQL query. Example for case duration in minutes: \n SELECT\n    (CAST(strftime('%s', MAX([time:timestamp])) AS FLOAT) - \n     CAST(strftime('%s', MIN([time:timestamp])) AS FLOAT)) / 60\nFROM\n    trace",                                               
                                                ),
                                            ], id='sql-input-dv-container-rp', style={'display': 'none'}),
                                        ]),
                                ])
                            ]
                        )
                ]),
                html.Div(
                    id='select-time-container',
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
                                    className='flex-row margin-left',
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
                                                id='date-from-rp',
                                                min_date_allowed=pd.Timestamp('1995-08-05'),
                                                max_date_allowed=pd.Timestamp('2023-11-30'),
                                                initial_visible_month=pd.Timestamp('2023-11-30'),
                                                date=pd.Timestamp('2023-11-30')
                                            ),
                                            dmc.TimeInput(
                                                id='time-from-rp',
                                                className='margin-top-5',
                                                format="24",
                                                withSeconds=True,
                                                value=dt.datetime.combine(dt.date.today(), dt.time.min)
                                            ),
                                        ]),
                                        html.Div(
                                            className='margin-left-15',
                                            children=[
                                                html.P(
                                                    className='p-option-col',
                                                    children=[
                                                        'Time to ',
                                                        html.Span('*', style={'color': 'red'})
                                                    ]
                                                ),
                                                dcc.DatePickerSingle(
                                                    id='date-to-rp',
                                                    min_date_allowed=pd.Timestamp('1995-08-05'),
                                                    max_date_allowed=pd.Timestamp('2023-11-30'),
                                                    initial_visible_month=pd.Timestamp('2023-11-30'),
                                                    date=pd.Timestamp('2023-11-30')
                                                ),
                                                dmc.TimeInput(
                                                    id='time-to-rp',
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
                                                'Backwards scope ',
                                                html.Span('*', style={'color': 'red'})
                                            ]
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown-backwards-scope',
                                            className='width-100',
                                            options=[
                                                
                                            ]
                                        ),
                                        html.Div([
                                                html.P('Additional backwards scope:', className='p-option-col'),
                                                dcc.Input(id='input-individual-backwards-scope-rp', className='input hight-35', type='number', placeholder=' Backwards scope in MINUTES'),
                                        ], id='div-individual-backwards-scope', style={'display': 'none'}), 
                                ])
                            ]
                        ),
                        html.Div(
                            className='div-center-button',
                            children=[
                                dcc.Loading(
                                    id="loading-add-relationship",
                                    type="circle",
                                    children=[
                                        html.Button(
                                            'Add Resource-Performance Relationship',
                                            id='button-add-relationship',
                                            className='button-generate',
                                        )
                                    ]
                                )
                            ]
                        )
                ])
            ]),
            html.Div(
                id='div-relationship-panels',
                className='flex-row',
                children=[
                    dcc.Graph(
                        id='placeholder-chart',
                        className='width-95',
                        figure=go.Figure(layout={
                            'xaxis': {'visible': False},
                            'yaxis': {'visible': False},
                            'annotations': [{
                                'text': 'Select options and press "Add Resource-Performance Relationship".',
                                'xref': 'paper',
                                'yref': 'paper',
                                'showarrow': False,
                                'font': {
                                    'size': 16
                                }
                            }]
                        })
                    )
                ]
            )
    ])
])

@app.callback(
    Output('div-relationship-panels', 'children', allow_duplicate=True),
    Output('button-add-relationship', 'children'),
    Output('input-alert-rp', 'children'),
    Output('input-alert-rp', 'is_open'),
    Input('button-add-relationship', 'n_clicks'),
    [State('div-relationship-panels', 'children'),
     State('pickle_df_name', 'data'),
     State('dropdown-xes-select', 'value'),
     State('dropdown-sampling-strategy', 'value'),
     State('case-num-limit', 'value'),
     State('activity-num-limit', 'value'),
     State('dropdown-filter-attribute-select', 'value'),
     State('filter-attribute-value', 'value'),
     State('sampling-seed', 'value'),
     State('dropdown-iv-select', 'value'),
     State('dropdown-dv-select', 'value'),
     State('date-from-rp', 'date'),
     State('time-from-rp', 'value'),
     State('date-to-rp', 'date'),
     State('time-to-rp', 'value'),
     State('dropdown-backwards-scope', 'value'),
     State('input-individual-backwards-scope-rp', 'value'),
     State('input-iv-sql-query-rp', 'value'),
     State('input-concept-name-rp', 'value'),
     State('input-resource-name-rp', 'value'),
     State('input-dv-sql-query-rp', 'value')], 
     prevent_initial_call=True
)
def add_panel(n_clicks, old_panel_children, pickle_df_name, xes_select_value, sampling_strategy_value, case_limit_value, activity_limit_value, filter_event_attribute, filter_event_value, seed_value, independent_variable_value, dependent_variable_value, date_from_str, time_from_str, date_to_str, time_to_str, backwards_scope_value, backwards_scope_individual, iv_sql, iv_concept_name, iv_resource_name, dv_sql):

    # check for None values
    if pickle_df_name is None:
        return no_update, no_update, 'Select XES file before adding a new resource-performance relationship!', True
    if any(var is None for var in [sampling_strategy_value, seed_value, independent_variable_value, dependent_variable_value, date_from_str, time_from_str, date_to_str, time_to_str, backwards_scope_value]):
        return no_update, no_update, 'Input all required fields (*) before adding a new resource-performance relationship!', True  
    if independent_variable_value == 'rbi_sql'  and (iv_sql == '' or iv_sql is None):
        return no_update, no_update, 'Input a custom sql statement for the IV before adding a resource-performance relationship!', True
    if independent_variable_value == 'rbi_activity_frequency'  and (iv_concept_name == '' or iv_concept_name is None):
        return no_update, no_update, 'Input an activity name before adding a resource-performance relationship!', True
    if independent_variable_value == 'rbi_interaction_two_resources'  and (iv_resource_name == '' or iv_resource_name is None):
        return no_update, no_update, 'Input a resource id before adding a resource-performance relationship!', True
    if dependent_variable_value == 'perf_sql'  and (dv_sql == '' or dv_sql is None):
        return no_update, no_update, 'Input a custom sql statement for the DV before adding a resource-performance relationship!', True
    
    df_event_log = load_from_pickle(pickle_df_name)
    
    timestamp_from_str = date_from_str + 'T' + time_from_str.split('T')[1] + '+00:00'
    timestamp_to_str = date_to_str + 'T' + time_to_str.split('T')[1] + '+00:00'

    timestamp_from = pd.Timestamp(timestamp_from_str)
    timestamp_to = pd.Timestamp(timestamp_to_str)

    rbi_function_mapping = {
        'rbi_sql': (sql_to_rbi, [iv_sql], 'Custom RBI (SQL)'),
        'rbi_distinct_activities': (rbi_distinct_activities, [], 'Distinct activities'),
        'rbi_activity_frequency': (rbi_activity_fequency, [iv_concept_name], 'Activity frequency'),
        'rbi_activity_completions': (rbi_activity_completions, [], 'Activity completions'),
        'rbi_case_completions': (rbi_case_completions, [], 'Case completions'),
        'rbi_fraction_case_completion': (rbi_fraction_case_completions, [], 'Fraction case completion'),
        'rbi_average_workload': (rbi_average_workload, [], 'Average workload'),
        'rbi_multitasking': (rbi_multitasking, [], 'Multitasking'),
        'rbi_average_duration_activity': (rbi_average_duration_activity, [], 'Average duration activity'),
        'rbi_interaction_two_resources': (rbi_interaction_two_resources, [iv_resource_name], 'Interaction two resources'),
        'rbi_social_position': (rbi_social_position, [], 'Social position')
    }
    rbi_function, additional_rbi_arguments, rbi_label = rbi_function_mapping.get(independent_variable_value, (None, [], ''))    

    performance_function_mapping = {
        'perf_sql': (sql_to_case_performance_metric, [dv_sql], 'Custom Performance Metric (SQL)'),
        'perf_case_duration': (case_duration, [], 'Case duration (min)'),
        'perf_activity_duration': (activity_duration, [], 'Activity duration (min)')
    }
    performance_function, additional_performance_arguments, performance_label = performance_function_mapping.get(dependent_variable_value, (None, [], ''))

    sampling_strategy_mapping = {
        'activity_level': 'Activity level sampling',
        'case_level': 'Case level sampling'
    }
    sampling_strategy_label = sampling_strategy_mapping.get(sampling_strategy_value, '')
    
    scope_mapping = {
        'activity_level': {
            'activity': (ScopeActivity.ACTIVITY, 'Activity scope'),
            'individual': (ScopeActivity.INDIVIDUAL, 'Individual scope'),
            'total': (ScopeActivity.TOTAL, 'Total scope')
        },
        'case_level': {
            'case': (ScopeCase.CASE, 'Case scope'),
            'individual': (ScopeCase.INDIVIDUAL, 'Individual scope'),
            'total': (ScopeCase.TOTAL, 'Total scope')
        }
    }
    backwards_scope, backwards_scope_label = scope_mapping.get(sampling_strategy_value, {}).get(backwards_scope_value, (ScopeActivity.TOTAL, 'Total scope'))
    if backwards_scope_individual is None or backwards_scope_individual == '':
        individual_scope_value = pd.Timedelta(0)
    else:
        individual_scope_value = pd.Timedelta(minutes=backwards_scope_individual)

    if sampling_strategy_value == 'case_level':
        if case_limit_value is None:
            return no_update, no_update, 'Input Max. number of cases before generating!', True
        if case_limit_value < 2:
            return no_update, no_update, 'The number of cases has to be larger than 1!', True
        rbi_values, perf_values = sample_regression_data_case(df_event_log, timestamp_from, timestamp_to, case_limit_value, seed_value, backwards_scope, rbi_function, performance_function, additional_rbi_arguments, additional_performance_arguments, individual_scope=individual_scope_value)
        count_str = str(len(rbi_values)) + '/' + str(case_limit_value) + ' cases'
    elif sampling_strategy_value == 'activity_level':
        if activity_limit_value is None:
            return no_update, no_update, 'Input Max. number of activities before generating!', True
        if activity_limit_value < 2:
            return no_update, no_update, 'The number of activities has to be larger than 1!', True
        rbi_values, perf_values = sample_regression_data_activity(df_event_log, timestamp_from, timestamp_to, filter_event_attribute, filter_event_value, activity_limit_value, seed_value, backwards_scope, rbi_function, performance_function, additional_rbi_arguments, additional_performance_arguments, individual_scope=individual_scope_value)
        count_str = str(len(rbi_values)) + '/' + str(activity_limit_value) + ' activities'

    if len(rbi_values) == 0:
        return no_update, no_update, 'Filter results in 0 selected cases/activities, change the inputs!', True
    
    _, _, r_squared, rpi_p_value, rpi_t_stat = fit_regression(rbi_values, perf_values)

    fig = px.scatter(x=rbi_values, y=perf_values, trendline="ols")
    fig.update_layout(margin=dict(l=30, r=30, t=50, b=70))
    fig.update_xaxes(title_text=rbi_label)
    fig.update_yaxes(title_text=performance_label)

    new_panel_id = str(uuid.uuid4())

    new_panel = html.Div(
                id = new_panel_id,
                children=[
                    dcc.Markdown(
                        children='**File:** ' + xes_select_value + '.xes',
                    ),
                    dcc.Markdown(
                        children='**SS:** ' + sampling_strategy_label,
                    ),
                    dcc.Markdown(
                        children='**Num/Max:** ' + count_str + ' (Seed: ' + str(seed_value) + ')',
                    ),
                    dcc.Markdown(
                        children='**IV:** ' + rbi_label,
                    ),
                    dcc.Markdown(
                        children='**DV:** ' + performance_label,
                    ),
                    dcc.Markdown(
                        children='**Date:** ' + f"{timestamp_from.strftime('%m/%d/%Y')} - {timestamp_to.strftime('%m/%d/%Y')}",
                    ),
                    dcc.Markdown(
                        children='**BS:** ' + backwards_scope_label,
                    ),
                    dcc.Graph(figure=fig),
                    dcc.Markdown(
                        className='',
                        children='**R-squared:** ' + str(round(r_squared, 8)),
                    ),
                    dcc.Markdown(
                        className='',
                        children='**p-value:** ' + str(format(rpi_p_value, '.8e')),
                    ),
                    dcc.Markdown(
                        className='',
                        children='**t-statistics:** ' + str(round(rpi_t_stat, 8)),
                    ),
                    html.Button('Delete', id={'type': 'delete-button', 'id': new_panel_id}, className='button-default margin-top', n_clicks=0)
            ])
    
    # delete placeholder panel if present
    old_panel_children = [child for child in old_panel_children if child.get('props', {}).get('id') != 'placeholder-chart']
    # set new panels
    if len(old_panel_children) == 0:
        new_panel = html.Div(className='div-rbi-relationship-panel width-95 flex-col', id=new_panel.id, children=new_panel.children)
        new_panel_children = [new_panel]
        return new_panel_children, no_update, no_update, no_update
    elif len(old_panel_children) == 1:
        new_panel = html.Div(className='div-rbi-relationship-panel width-45 flex-col', id=new_panel.id, children=new_panel.children)
        old_panel_child = html.Div(className='div-rbi-relationship-panel width-45 flex-col', id=old_panel_children[0]['props']['id'], children=old_panel_children[0]['props']['children'])
        new_panel_children = [new_panel] + [old_panel_child]
        return new_panel_children, no_update, no_update, no_update
    elif len(old_panel_children) >= 2:
        new_panel = html.Div(className='div-rbi-relationship-panel width-30 flex-col', id=new_panel.id, children=new_panel.children)
        new_panel_children = [new_panel]
        for old_panel_child in old_panel_children:
            old_panel_child = html.Div(className='div-rbi-relationship-panel width-30 flex-col', id=old_panel_child['props']['id'], children=old_panel_child['props']['children'])
            new_panel_children += [old_panel_child]
        return new_panel_children[:3], no_update, no_update, no_update

# Delete a resource-performance analysis panel
@app.callback(
    Output('div-relationship-panels', 'children', allow_duplicate=True),
    [Input({'type': 'delete-button', 'id': ALL}, 'n_clicks')],
    [State('div-relationship-panels', 'children')],
    prevent_initial_call=True
)
def delete_panel(n_clicks, panels):
    ctx = callback_context

    if not ctx.triggered:
        return no_update

    # Determine which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    delete_id = json.loads(button_id)['id']

    # Check if the button was actually clicked
    if not any(click > 0 for click in n_clicks):
        return no_update

    # Remove the corresponding panel
    rest_panels = [panel for panel in panels if 'props' in panel and 'id' in panel['props'] and panel['props']['id'] != delete_id]

    if len(rest_panels) == 0:
        return rest_panels
    elif len(rest_panels) == 1:
        className_str = 'div-rbi-relationship-panel width-95 flex-col'
    elif len(rest_panels) == 2:
        className_str = 'div-rbi-relationship-panel width-45 flex-col'
    elif len(rest_panels) == 3:
        className_str = 'div-rbi-relationship-panel width-30 flex-col'
    
    sized_panel_children = []
    for panel in rest_panels:
        sized_panel_child = html.Div(className=className_str, id=panel['props']['id'], children=panel['props']['children'])
        sized_panel_children += [sized_panel_child]

    if len(sized_panel_children) > 3:
        return sized_panel_children[:3]

    return sized_panel_children

# update input fields based on sampling strategy 
@app.callback(
    [Output('dropdown-dv-select', 'options'),
     Output('dropdown-backwards-scope', 'options'),
     Output('div-max-cases', 'style'),
     Output('div-max-activities', 'style'),
     Output('div-seed', 'style'),
     Output('div-filter-attribute-select', 'style'),
     Output('div-filter-attribute-value', 'style')],
    Input('dropdown-sampling-strategy', 'value')
)
def update_resource_options(sampling_strategy):
    if sampling_strategy == 'activity_level':
        dv_options = [
            {'label': 'Activity duration', 'value': 'perf_activity_duration'},
        ]
        scope_options = [
            {'label': 'Activity scope', 'value': 'activity'},
            {'label': 'Individual scope', 'value': 'individual'},
            {'label': 'Total scope', 'value': 'total'},
        ]
        div_max_cases_style = {'display': 'none'} 
        div_max_activities_style = {'display': 'block'}
        div_seed_style = {'display': 'block'}
        div_attribute_select_style = {'display': 'block'}
        div_attribute_value_style = {'display': 'block'}
    elif sampling_strategy == 'case_level':
        dv_options = [
            {'label': 'Custom Performance Metric (SQL)', 'value': 'perf_sql'},
            {'label': 'Case duration', 'value': 'perf_case_duration'},
        ]
        scope_options = [
            {'label': 'Case scope', 'value': 'case'},
            {'label': 'Individual scope', 'value': 'individual'},
            {'label': 'Total scope', 'value': 'total'},
        ]
        div_max_cases_style = {'display': 'block'} 
        div_max_activities_style = {'display': 'none'}
        div_seed_style = {'display': 'block'}
        div_attribute_select_style = {'display': 'none'}
        div_attribute_value_style = {'display': 'none'}
    else:
        scope_options = no_update
        div_max_cases_style = {'display': 'none'} 
        div_max_activities_style = {'display': 'none'}
        div_seed_style = {'display': 'none'}
        div_attribute_select_style = {'display': 'none'}
        div_attribute_value_style = {'display': 'none'}

    return [dv_options, scope_options, div_max_cases_style, div_max_activities_style, div_seed_style, div_attribute_select_style, div_attribute_value_style]

# set values based on XES file
@app.callback(
    [Output('date-from-rp', 'min_date_allowed'),
     Output('date-from-rp', 'max_date_allowed'),
     Output('date-from-rp', 'initial_visible_month'),
     Output('date-from-rp', 'date'),
     Output('time-from-rp', 'value'),
     Output('date-to-rp', 'min_date_allowed'),
     Output('date-to-rp', 'max_date_allowed'),
     Output('date-to-rp', 'initial_visible_month'),
     Output('date-to-rp', 'date'),
     Output('time-to-rp', 'value'),
     Output('case-num-limit', 'value'),
     Output('activity-num-limit', 'value'),
     Output('dropdown-filter-attribute-select', 'options'),],
    Input('pickle_df_name', 'data')
)
def update_resource_options(pickle_df_name):
    if pickle_df_name:
        df_event_log = load_from_pickle(pickle_df_name)
        
        earliest_timestamp = get_earliest_timestamp(df_event_log)
        latest_timestamp = get_latest_timestamp(df_event_log)

        earliest_date = earliest_timestamp.date()
        latest_date = latest_timestamp.date()

        earliest_time = earliest_timestamp.time()
        latest_time = latest_timestamp.time()

        earliest_datetime = dt.datetime.combine(earliest_date, earliest_time)
        latest_datetime = dt.datetime.combine(latest_date, latest_time)

        case_count = count_unique_cases(df_event_log)
        event_count = count_completed_events(df_event_log)

        attribute_options = [{'label': col, 'value': col} for col in get_column_names(df_event_log)]

        return [earliest_date, latest_date, earliest_date, earliest_date, earliest_datetime, earliest_date, latest_date, latest_date, latest_date, latest_datetime, case_count, event_count, attribute_options]
    else:
        # Return an empty list if no file is selected
        return [no_update] * 13

# toggle the visibility of iv input fields  
@app.callback(
    [Output('sql-input-iv-container-rp', 'style'),
     Output('concept-name-input-container-rp', 'style'),
     Output('resource-id-input-container-rp', 'style')],
    Input('dropdown-iv-select', 'value')
)
def toggle_rbi_input_fields_visibility(selected_rbi):
    inputs_visibility = [{'display': 'none'}] * 3 # set to number of input containers

    if selected_rbi == 'rbi_sql':
        inputs_visibility[0] = {'display': 'block'} 
    elif selected_rbi == 'rbi_activity_frequency' or selected_rbi =='rbi_average_duration_activity':
        inputs_visibility[1] = {'display': 'block'}
    elif selected_rbi == 'rbi_interaction_two_resources':
        inputs_visibility[2] = {'display': 'block'}
    
    return inputs_visibility

# toggle the visibility of iv input fields  
@app.callback(
    [Output('sql-input-dv-container-rp', 'style')],
    Input('dropdown-dv-select', 'value')
)
def toggle_perf_input_fields_visibility(selected_perf):
    inputs_visibility = [{'display': 'none'}] * 1 # set to number of input containers

    if selected_perf == 'perf_sql':
        inputs_visibility[0] = {'display': 'block'} 
    
    return inputs_visibility

# Callback to show/hide the individual backwards scope input
@app.callback(
    Output('div-individual-backwards-scope', 'style'),
    Input('dropdown-backwards-scope', 'value')
)
def toggle_individual_backwards_scope(selected_value):
    if selected_value == 'individual':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

