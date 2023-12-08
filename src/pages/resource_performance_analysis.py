from app import app
import pandas as pd
from dash import html, State, Input, Output, dcc, no_update

# Define the page layout
layout = html.Div([
    html.Div(
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
                                            id='dropdown-iv-select',
                                            options=[
                                                {'label': 'Custom Performance Metric (SQL)', 'value': 'perf_sql'},
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
                        ])
                ])
            ]),
    ])
])