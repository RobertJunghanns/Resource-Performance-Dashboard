import pandas as pd
import numpy as np

from app import app
from dash import html, Input, Output, State, dcc, no_update
import plotly.express as px

from model.utility.pickle_utility import load_from_pickle
from model.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp
from model.sampling.case_level_sampling import ScopeCase, sample_regression_data_case
from model.sampling.activity_level_sampling import ScopeActivity
from model.measures.resource_behavior_indicators import sql_to_rbi, rbi_distinct_activities, rbi_activity_fequency, rbi_activity_completions, rbi_case_completions, rbi_fraction_case_completions, rbi_average_workload, rbi_multitasking, rbi_average_duration_activity, rbi_average_case_duration, rbi_interaction_two_resources, rbi_social_position
from model.measures.process_performance_measures import sql_to_performance_metric, case_duration
from model.regression_analysis import fit_regression

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
                                        {'label': 'Activity level sampling', 'value': 'activity_level'},
                                        {'label': 'Case level sampling', 'value': 'case_level'},
                                    ]
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
                                                {'label': 'Average case duration', 'value': 'rbi_average_duration_case'},
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
                                                    placeholder="Enter SQL query.",                                               
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
                                ])
                            ]
                        ),
                        html.Div(
                            className='div-center-button',
                            children=[
                                html.Button(
                                    'Add Resource-Performance Relationship',
                                    id='button-add-relationship'
                                ) 
                        ])
                ])
            ]),
            html.Div(
                id='div-relationship-panels',
                className='flex-row',
                children=[
                    html.Div(
                        className='div-rbi-relationship-panel flex-col',
                        children=[
                            dcc.Markdown(
                                className='',
                                children='**SS:** Case level Sampling',
                            ),
                            dcc.Markdown(
                                className='',
                                children='**IV: Fraction case completion**',
                            ),
                            dcc.Markdown(
                                className='',
                                children='**DV: Case duration**',
                            ),
                            dcc.Markdown(
                                className='',
                                children='**Date:** 11/30/2023 - 11/30/2023',
                            ),
                            dcc.Markdown(
                                className='',
                                children='**BS:** Individual Scope',
                            ),
                            dcc.Graph(id='graph-0'),
                            # px.scatter(
                            #     df, x='total_bill', y='tip', opacity=0.65,
                            #     trendline='ols', trendline_color_override='darkblue'
                            # )
                            # model = LinearRegression()
                            # model.fit(X_train, y_train)

                            # x_range = np.linspace(X.min(), X.max(), 100)
                            # y_range = model.predict(x_range.reshape(-1, 1))


                            # fig = go.Figure([
                            #     go.Scatter(x=X_train.squeeze(), y=y_train, name='train', mode='markers'),
                            #     go.Scatter(x=X_test.squeeze(), y=y_test, name='test', mode='markers'),
                            #     go.Scatter(x=x_range, y=y_range, name='prediction')
                            # ])
                            dcc.Markdown(
                                className='',
                                children='**R-squared:** 0.287',
                            ),
                            dcc.Markdown(
                                className='',
                                children='**p-value:** 0.187',
                            ),
                            dcc.Markdown(
                                className='',
                                children='**t-statistics:** 0.187',
                            ),
                    ]),
            ])
    ])
])


@app.callback(
    Output('div-relationship-panels', 'children'),
    Input('button-add-relationship', 'n_clicks'),
    [State('pickle_df_name', 'data'),
     State('dropdown-sampling-strategy', 'value'),
     State('dropdown-iv-select', 'value'),
     State('dropdown-dv-select', 'value'),
     State('date-from-rp', 'date'),
     State('date-to-rp', 'date'),
     State('dropdown-backwards-scope', 'value'),
     State('input-iv-sql-query-rp', 'value'),
     State('input-concept-name-rp', 'value'),
     State('input-resource-name-rp', 'value'),
     State('input-dv-sql-query-rp', 'value')]
)
def update_panels(n_clicks, pickle_df_name, sampling_strategy_value, independent_variable_value, dependent_variable_value, date_from_str, date_to_str, backwards_scope_value, iv_sql, iv_concept_name, iv_resource_name, dv_sql):
    
    
    df_event_log = load_from_pickle(pickle_df_name)
    date_from = pd.to_datetime(date_from_str)
    date_to = pd.to_datetime(date_to_str)

    rbi_function_mapping = {
        'rbi_sql': (sql_to_rbi, [iv_sql], 'Custom RBI (SQL)'),
        'rbi_distinct_activities': (rbi_distinct_activities, [], 'Distinct activities'),
        'rbi_activity_frequency': (rbi_activity_fequency, [iv_concept_name], 'Activity frequency'),
        'rbi_activity_completions': (rbi_activity_completions, [], 'Activity completions'),
        'rbi_case_completions': (rbi_activity_completions, [], 'Case completions'),
        'rbi_fraction_case_completion': (rbi_fraction_case_completions, [], 'Fraction case completion'),
        'rbi_average_workload': (rbi_average_workload, [], 'Average workload'),
        'rbi_multitasking': (rbi_multitasking, [], 'Multitasking'),
        'rbi_average_duration_activity': (rbi_average_duration_activity, [], 'Average duration activity'),
        'rbi_average_duration_case': (rbi_average_case_duration, [], 'Average case duration'),
        'rbi_interaction_two_resources': (rbi_interaction_two_resources, [iv_resource_name], 'Interaction two resources'),
        'rbi_social_position': (rbi_social_position, [], 'Social position')
    }
    rbi_function, additional_rbi_arguments, rbi_label = rbi_function_mapping.get(independent_variable_value, (None, [], ''))
    
    performance_function_mapping = {
        'perf_sql': (sql_to_performance_metric, [dv_sql], 'Custom Performance Metric (SQL)'),
        'perf_case_duration': (case_duration, [], 'Case duration')
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
    print(sampling_strategy_value)
    print(scope_mapping.get(sampling_strategy_value, {}))
    print(scope_mapping.get(sampling_strategy_value, {}).get(backwards_scope_value, (ScopeActivity.TOTAL, 'Total scope')))
    backwards_scope, backwards_scope_label = scope_mapping.get(sampling_strategy_value, {}).get(backwards_scope_value, (ScopeActivity.TOTAL, 'Total scope'))

    if sampling_strategy_value == 'case_level':
        rbi_values, perf_values = sample_regression_data_case(df_event_log, date_from, date_to, backwards_scope, rbi_function, performance_function, *additional_rbi_arguments, *additional_performance_arguments) #, individual_scope
    # elif sampling_strategy_value == 'activity_level':
    #     sample_regression_data_case(df_event_log, date_from, date_to, backwards_scope, )
    else:
        return no_update 
    
    _, _, r_squared, rpi_p_value, rpi_t_stat = fit_regression(rbi_values, perf_values)

    #x_range = np.linspace(rbi_values.min(), rbi_values.max(), 100)
    #y_range = slope * x_range + intercept

    fig = px.scatter(x=rbi_values, y=perf_values, trendline="ols")

    new_panel = html.Div(
                className='div-rbi-relationship-panel flex-col',
                children=[
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
                    dcc.Graph(id='graph-0', figure=fig),
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
            ])
   
    #check number of panels
    #get children
    #if number < x append else delete lowest id and append (in the front)
    
    return new_panel

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