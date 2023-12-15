import pandas as pd
import numpy as np
import uuid
import json

from app import app
from dash import html, Input, Output, State, dcc, no_update, ALL, callback_context
import plotly.express as px
import dash_bootstrap_components as dbc

from model.utility.pickle_utility import load_from_pickle
from model.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp
from model.sampling.case_level_sampling import ScopeCase, sample_regression_data_case
from model.sampling.activity_level_sampling import ScopeActivity
from model.measures.resource_behavior_indicators import sql_to_rbi, rbi_distinct_activities, rbi_activity_fequency, rbi_activity_completions, rbi_case_completions, rbi_fraction_case_completions, rbi_average_workload, rbi_multitasking, rbi_average_duration_activity, rbi_interaction_two_resources, rbi_social_position
from model.measures.case_performance_measures import sql_to_case_performance_metric, case_duration
from model.regression_analysis import fit_regression

panel_id=0

# Define the page layout
layout = html.Div([
    html.Div(
        className='flex-row',
        id='page-resource-performance',
        children = [
            html.Div(
            className='div-rp-sidebar',
            children = [
                html.Div(
                    className='div-div-rp-sidebar flex-row',
                    children = [
                        html.Div(
                            className="div-logo",
                            children=html.Img(
                                id='img-sample',
                                className="", src=("./assets/images/sample.png"),
                            ), 
                        ),
                        html.Div(
                            className='div-selection',
                            children = [
                                html.P(
                                    className='p-option-col',
                                    children='Sampling Strategy:', 
                                ),
                                dcc.Dropdown(
                                    id='dropdown-sampling-strategy',
                                    options=[
                                        #{'label': 'Activity level sampling', 'value': 'activity_level'},
                                        {'label': 'Case level sampling', 'value': 'case_level'},
                                    ],
                                    value='case_level'
                                ),
                        ])
                ]),
                html.Div(
                    id='select-relationship-container',
                    className='div-div-rp-sidebar flex-col',
                    children = [
                        html.Div(
                            id='select-rbi-iv',
                            className='flex-row',
                            children=[
                                html.Div(
                                    className="div-logo",
                                    children=html.Img(
                                        id='img-rbi',
                                        className="", src=("./assets/images/rbi.png"),
                                    ), 
                                ),
                                html.Div(
                                    className='div-selection',
                                    children=[
                                        html.P(
                                            className='p-option-col',
                                            children='Independent Variable (RBI):', 
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
                                                html.P('SQL query:', className='p-option-col'),
                                                dcc.Textarea(
                                                    id='input-iv-sql-query-rp',
                                                    className='sql-input',
                                                    placeholder="Enter SQL query. Example for activity frequency:\nSELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)\n   FROM (\n      SELECT\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = 'resource_id'\n         AND [concept:name] = '09_AH_I_010')\n         AS activity,\n         (SELECT COUNT([concept:name])\n         FROM event_log\n         WHERE [org:resource] = 'resource_id')\n         AS all_activities\n   ) AS count",
                                                ),
                                            ], id='sql-input-iv-container-rp', style={'display': 'none'}),
                                            html.Div([
                                                html.P('Activity name:', className='p-option-col'),
                                                dcc.Input(id='input-concept-name-rp', className='input-concept-name', type='text', placeholder=' Enter concept:name...'),
                                            ], id='concept-name-input-container-rp', style={'display': 'none'}), 
                                            html.Div([
                                                html.P('Interaction resource id:', className='p-option-col'),
                                                dcc.Input(id='input-resource-name-rp', className='input-resource-name', type='text', placeholder=' Enter org:resource...'),
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
                                        className="", src=("./assets/images/down-arrow.png"),
                                    ),
                                ),
                            ]
                        ),
                        html.Div(
                            id='select-performance-dv',
                            className='flex-row',
                            children=[
                                html.Div(
                                    className="div-logo",
                                    children=html.Img(
                                        id='img-performance',
                                        className="", src=("./assets/images/performance.png"),
                                    ), 
                                ),
                                html.Div(
                                    className='div-selection',
                                    children=[
                                        html.P(
                                            className='p-option-col',
                                            children='Dependent Variable (Performance Metric):', 
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown-dv-select',
                                            options=[
                                                {'label': 'Custom Performance Metric (SQL)', 'value': 'perf_sql'},
                                                {'label': 'Case duration', 'value': 'perf_case_duration'},
                                            ]
                                        ),
                                        html.Div([
                                            html.Div([
                                                html.P('SQL query:', className='p-option-col'),
                                                dcc.Textarea(
                                                    id='input-dv-sql-query-rp',
                                                    className='sql-input',
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
                    className='div-div-rp-sidebar flex-row',
                    children = [
                        html.Div(
                            className="div-logo",
                            children=html.Img(
                                id='img-calendar',
                                className="", src=("./assets/images/calendar.png"),
                            ), 
                        ),
                        html.Div(
                            className='flex-col',
                            children=[
                                html.Div(
                                    className='div-time-selection flex-row',
                                    children=[
                                        html.Div([
                                            html.P(
                                                className='p-option-col',
                                                children='Date from:',
                                            ),
                                            dcc.DatePickerSingle(
                                                id='date-from-rp',
                                                min_date_allowed=pd.Timestamp('1995-08-05'),
                                                max_date_allowed=pd.Timestamp('2023-11-30'),
                                                initial_visible_month=pd.Timestamp('2023-11-30'),
                                                date=pd.Timestamp('2023-11-30')
                                            ),
                                        ]),
                                        html.Div(
                                            id='div-second-date',
                                            children=[
                                                html.P(
                                                    className='p-option-col',
                                                    children='Date up to:',
                                                ),
                                                dcc.DatePickerSingle(
                                                    id='date-to-rp',
                                                    min_date_allowed=pd.Timestamp('1995-08-05'),
                                                    max_date_allowed=pd.Timestamp('2023-11-30'),
                                                    initial_visible_month=pd.Timestamp('2023-11-30'),
                                                    date=pd.Timestamp('2023-11-30')
                                                ),
                                        ]),
                                ]),
                                html.Div(
                                    className='div-time-selection',
                                    children=[
                                        html.P(
                                            className='p-option-col',
                                            children='Backwards scope:',
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown-backwards-scope',
                                            options=[
                                                
                                            ]
                                        ),
                                        html.Div([
                                                html.P('Individual backwards scope:', className='p-option-col'),
                                                dcc.Input(id='input-individual-backwards-scope-rp', className='input-concept-name', type='number', placeholder=' Backwards scope in MINUTES'),
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
                                            id='button-add-relationship'
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
                children=[]
            )
    ])
])

# Add a resource-performance analysis panel
@app.callback(
    Output('div-relationship-panels', 'children', allow_duplicate=True),
    Output('button-add-relationship', 'children'),
    Input('button-add-relationship', 'n_clicks'),
    [State('div-relationship-panels', 'children'),
     State('pickle_df_name', 'data'),
     State('dropdown-xes-select', 'value'),
     State('dropdown-sampling-strategy', 'value'),
     State('dropdown-iv-select', 'value'),
     State('dropdown-dv-select', 'value'),
     State('date-from-rp', 'date'),
     State('date-to-rp', 'date'),
     State('dropdown-backwards-scope', 'value'),
     State('input-individual-backwards-scope-rp', 'value'),
     State('input-iv-sql-query-rp', 'value'),
     State('input-concept-name-rp', 'value'),
     State('input-resource-name-rp', 'value'),
     State('input-dv-sql-query-rp', 'value')], 
     prevent_initial_call=True
)
def add_panel(n_clicks, old_panel_children, pickle_df_name, xes_select_value, sampling_strategy_value, independent_variable_value, dependent_variable_value, date_from_str, date_to_str, backwards_scope_value, backwards_scope_individual, iv_sql, iv_concept_name, iv_resource_name, dv_sql):
    
    if xes_select_value is None or xes_select_value == '':
        return no_update, no_update
    
    df_event_log = load_from_pickle(pickle_df_name)
    date_from = pd.to_datetime(date_from_str)
    date_to = pd.to_datetime(date_to_str)

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
        'perf_case_duration': (case_duration, [], 'Case duration (min)')
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
        rbi_values, perf_values = sample_regression_data_case(df_event_log, date_from, date_to, backwards_scope, rbi_function, performance_function, additional_rbi_arguments, additional_performance_arguments, individual_scope=individual_scope_value)
    # elif sampling_strategy_value == 'activity_level':
    #     sample_regression_data_case(df_event_log, date_from, date_to, backwards_scope, )
    else:
        return no_update, no_update
    
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
                        className='',
                        children='**File:** ' + xes_select_value + '.xes',
                    ),
                    dcc.Markdown(
                        className='',
                        children='**SS:** ' + sampling_strategy_label,
                    ),
                    dcc.Markdown(
                        className='',
                        children='**IV:** ' + rbi_label,
                    ),
                    dcc.Markdown(
                        className='',
                        children='**DV:** ' + performance_label,
                    ),
                    dcc.Markdown(
                        className='',
                        children='**Date:** ' + f"{date_from.strftime('%m/%d/%Y')} - {date_to.strftime('%m/%d/%Y')}",
                    ),
                    dcc.Markdown(
                        className='',
                        children='**BS:** ' + backwards_scope_label,
                    ),
                    dcc.Graph(figure=fig),
                    dcc.Markdown(
                        className='',
                        children='**R-squared:** ' + str(r_squared),
                    ),
                    dcc.Markdown(
                        className='',
                        children='**p-value:** ' + str(rpi_p_value),
                    ),
                    dcc.Markdown(
                        className='',
                        children='**t-statistics:** ' + str(rpi_t_stat),
                    ),
                    html.Button('Delete', id={'type': 'delete-button', 'id': new_panel_id}, className='button-default margin-top', n_clicks=0)
            ])
    if len(old_panel_children) == 0:
        new_panel = html.Div(className='div-rbi-relationship-panel width-95 flex-col', id=new_panel.id, children=new_panel.children)
        new_panel_children = [new_panel]
        return new_panel_children, no_update
    elif len(old_panel_children) == 1:
        new_panel = html.Div(className='div-rbi-relationship-panel width-45 flex-col', id=new_panel.id, children=new_panel.children)
        old_panel_child = html.Div(className='div-rbi-relationship-panel width-45 flex-col', id=old_panel_children[0]['props']['id'], children=old_panel_children[0]['props']['children'])
        new_panel_children = [new_panel] + [old_panel_child]
        return new_panel_children, no_update
    elif len(old_panel_children) >= 2:
        new_panel = html.Div(className='div-rbi-relationship-panel width-30 flex-col', id=new_panel.id, children=new_panel.children)
        new_panel_children = [new_panel]
        for old_panel_child in old_panel_children:
            old_panel_child = html.Div(className='div-rbi-relationship-panel width-30 flex-col', id=old_panel_child['props']['id'], children=old_panel_child['props']['children'])
            new_panel_children += [old_panel_child]
        return new_panel_children[:3], no_update

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
    
@app.callback(
    [Output('dropdown-backwards-scope', 'options')],
    Input('dropdown-sampling-strategy', 'value')
)
def update_resource_options(sampling_strategy):
    if sampling_strategy == 'activity_level':
        options = [
            {'label': 'Activity scope', 'value': 'activity'},
            {'label': 'Individual scope', 'value': 'individual'},
            {'label': 'Total scope', 'value': 'total'},
        ]
    elif sampling_strategy == 'case_level':
        options = [
            {'label': 'Case scope', 'value': 'case'},
            {'label': 'Individual scope', 'value': 'individual'},
            {'label': 'Total scope', 'value': 'total'},
        ]
    else:
        options = no_update

    return [options]

@app.callback(
    [Output('date-from-rp', 'min_date_allowed'),
     Output('date-from-rp', 'max_date_allowed'),
     Output('date-from-rp', 'initial_visible_month'),
     Output('date-from-rp', 'date'),
     Output('date-to-rp', 'min_date_allowed'),
     Output('date-to-rp', 'max_date_allowed'),
     Output('date-to-rp', 'initial_visible_month'),
     Output('date-to-rp', 'date'),],
    Input('pickle_df_name', 'data')
)
def update_resource_options(pickle_df_name):
    if pickle_df_name:
        df_event_log = load_from_pickle(pickle_df_name)
        
        earliest_dt = get_earliest_timestamp(df_event_log)
        latest_dt = get_latest_timestamp(df_event_log)

        return [earliest_dt, latest_dt, earliest_dt, earliest_dt, earliest_dt, latest_dt, latest_dt, latest_dt]
    else:
        # Return an empty list if no file is selected
        return [no_update] * 8

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

