import config
from app import app
from pages import resource_behavior
from pages import resource_performance

import base64
import dash
import pm4py
import json
import pandas as pd
import dash_bootstrap_components as dbc

from dash import html, dcc, Input, Output, State, ALL, callback_context, no_update
from pathlib import Path
from framework.utility.pickle_utility import save_as_pickle

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='pickle_df_name'),
    html.Div(
        id='header',
        children=[
            html.A(
                html.Div(
                    children=html.Img(
                        id='img-dashboard',
                        src="./assets/images/dashboard.png",
                    ),
                ),
                href="https://opendatabim.com/#", target="_blank",
            ),
            html.H2(
                id='header-title',
                children="Resource Performance Analysis for Event Logs", 
            ),
            html.A(
                id='box-github',
                children=[
                    'View on GitHub'
                ],
                href="https://github.com/RobertJunghanns/Resource-Performance-Dashboard"
            ),
            html.Div(
                id="div-github-logo",
                children=html.Img(
                    id='img-github',
                    className="logo", src=("./assets/images/github.png"),
                ), 
            ),
        ]
    ),
    dbc.Alert(id='upload-alert',className='margin-top', duration=4000, dismissable=True, is_open=False),
    html.Div(
        className='div-option-box',
        children=[
            html.Div(
                className='div-div-option-box',
                children = [
                    html.Div(
                    id='div-xes-upload',
                    children= [
                        html.Div([
                            html.P(
                                className='margin-left',
                                children='Upload XES file:', 
                            ),
                            dcc.Upload(
                                id='dcc-xes-upload',
                                children=html.Div([
                                    '📥 Drag and Drop or ',
                                    html.A('Select Files')
                                ]),
                                multiple=False
                            ),
                        ]),
                    ]),
                    html.Div(
                        id='div-xes-select',
                        children = [
                            html.P(
                                id='p-xes-select',
                                children=[
                                    'Select XES file: ',
                                    html.Span('*', style={'color': 'red'})
                                ]
                            ),
                            dcc.Dropdown(
                                id='dropdown-xes-select',
                                className='width-100',
                                options=[]
                            ),
                    ]),
                    dcc.Loading(
                        id='graph-loading-output',
                        children=[],
                        type="circle",
                        color='#2c5c97',
                        fullscreen=True
                    ),
            ]),
    ]),
    html.Div(
        className='div-option-box',
        children=[
            html.Div(
                className='div-div-option-box',
                children = [
                html.P(className='margin-left', children='Select page:'),
                html.Div(
                    id='div-buttons',
                    children=[
                        html.Button('Resource Behavior Analysis', id={'type': 'dynamic-button', 'index': 1}, className='button-default width-45 button-selected', style={'margin-right': '15px'}),
                        html.Button('Resource-Performance Analysis', id={'type': 'dynamic-button', 'index': 2}, className='button-default width-45'),
                ])
            ]),
    ]),
    html.Div(id='page-content', children=[])
])

@app.callback(
    [Output('pickle_df_name', 'data'),
     Output('graph-loading-output', 'children')],
    Input('dropdown-xes-select', 'value')
)
def set_global_variable(selected_filename):    
    if selected_filename is not None:
        current_file_path = Path(__file__).resolve().parent
        file_path = str(current_file_path / 'data' / (selected_filename + '.xes'))

        df_event_log = pm4py.read_xes(file_path)
        save_as_pickle(df_event_log, selected_filename)

        return selected_filename, None
    else:
        return None, None

# Define the callback for the upload component
@app.callback(
    [Output('upload-alert', 'children'),
    Output('upload-alert', 'color'),
    Output('upload-alert', 'is_open'),
    Output('dropdown-xes-select', 'options')],
    [Input('dcc-xes-upload', 'contents')],
    [State('dcc-xes-upload', 'filename')]
)
def upload_xes(contents, filename):
    current_file_path = Path(__file__).resolve().parent
    # Define the data directory path
    data_dir_path = current_file_path / 'data'
    # Create the data directory if it doesn't exist
    data_dir_path.mkdir(parents=True, exist_ok=True)
    # Initialize dropdown options
    dropdown_options = [{'label': file.name, 'value': file.stem} 
                                for file in data_dir_path.glob('*.xes')]
    if contents is not None:
        _, content_string = contents.split(',')
        if filename.endswith('.xes'):
            # Define the save_path using the data directory path
            save_path = data_dir_path / filename
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(content_string))

            # After saving, refresh the dropdown by getting all .xes files in the data directory
            dropdown_options = [{'label': file.name, 'value': file.stem} 
                                for file in data_dir_path.glob('*.xes')]

            return ("File uploaded successfully!", "success", True, dropdown_options)
        else:
            return ("File upload failed. This type is not supported. Please try again.", "danger", True, dropdown_options)
    return ("No file uploaded.", "warning", False, dropdown_options)


# ROUTING-1: Set url based on selected page
@app.callback(
    Output('url', 'pathname'),
    [Input({'type': 'dynamic-button', 'index': ALL}, 'n_clicks')],
)
def navigate(*args):
    ctx = callback_context

    if not ctx.triggered:
        return no_update

    # Determine which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_id = json.loads(button_id)

    url_map = {
        1: '/resource-behavior',
        2: '/resource-performance-analysis',
    }

    return url_map.get(button_id['index'], no_update)

# ROUTING-2: Supply page-content based on url
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/resource-behavior':
        return resource_behavior.layout
    if pathname == '/resource-performance-analysis':
        return resource_performance.layout
    else: # if redirected to unknown link
        return resource_behavior.layout

# ROUTING-3: Change button style based on selected page
@app.callback(
    [Output({'type': 'dynamic-button', 'index': ALL}, 'className')],
    [Input('url', 'pathname')],
    [State({'type': 'dynamic-button', 'index': ALL}, 'className')],
)
def update_button_classes(pathname, *args):
    if pathname == '/resource-behavior':
        button_id = {'type': 'dynamic-button', 'index': 1}
    if pathname == '/resource-performance-analysis':
         button_id = {'type': 'dynamic-button', 'index': 2}
    else: # if redirected to unknown link
         button_id = {'type': 'dynamic-button', 'index': 1}

    ctx = dash.callback_context
    button_states = ctx.states
    class_list = []

    for i in range(len(button_states)):   
        if button_id == {'type': 'dynamic-button', 'index': i+1}:
            class_list.append('button-default width-45 button-selected')
        else:
            class_list.append('button-default width-45')

    return [class_list]    


if __name__ == '__main__':
    app.run_server(debug=True, port=config.dash_port)