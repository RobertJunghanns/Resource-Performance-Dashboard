import pandas as pd

from app import app
from dash import html, Input, Output, State, dcc, no_update

from model.pickle_utility import load_from_pickle
from model.xes_utility import get_unique_resources, get_earliest_timestamp, get_latest_timestamp

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
     
     ]
)
def update_panels(n_clicks, pickle_df_name, sampling_strategy, ):

    df_event_log = load_from_pickle(pickle_df_name)
    #sample
    #get dv/iv
    #create figure
    #check number of panels
    #get children
    #if number < x append else delete lowest id and append (in the front)
    
    return html.Div(
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