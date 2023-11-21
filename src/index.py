from pages import resource_behavior, resource_performance_analysis
from model.xes_utility import df_to_json
from app import app

import base64
import dash
import pm4py
import json
import pandas as pd
import dash_bootstrap_components as dbc

from dash import html, dcc, Input, Output, State, ALL, callback_context, no_update
from pathlib import Path


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='json_event_log'),
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
                children="Resource-Performance Analysis for Event Logs", 
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
    dbc.Alert(id='upload-alert', duration=4000, dismissable=True, is_open=False),
    html.Div(
        className='div-option-box',
        children=[
            html.Div(
                className='div-in-option-box',
                children = [
                    html.Div(
                    id='div-xes-upload',
                    children= [
                        html.Div([
                            html.P(
                                id='p-xes-upload',
                                children='Upload XES file', 
                            ),
                            dcc.Upload(
                                id='dcc-xes-upload',
                                children=html.Div([
                                    '📥 Drag and Drop or ',
                                    html.A('Select Files')
                                ]),
                                # Allow multiple files to be uploaded
                                multiple=False
                            ),
                        ]),
                    ]),
                    html.Div(
                        id='div-xes-select',
                        children = [
                            html.P(
                                id='p-xes-select',
                                children='Select XES file', 
                            ),
                            dcc.Dropdown(
                                id='dropdown-xes-select',
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
                className='div-in-option-box',
                children = [
                html.P(id='p-page-select', children='Select page'),
                html.Div(
                    id='div-buttons',
                    children=[
                        #html.Button('Resource Behavior', id='button-resource-behavior', className='button-default'),
                        #html.Button('Resource-Performance Analysis', id= 'button-resource-performance-analysis', className='button-default')
                        html.Button('Resource Behavior', id={'type': 'dynamic-button', 'index': 1}, className='button-default'),
                        html.Button('Resource Performance Analysis', id={'type': 'dynamic-button', 'index': 2}, className='button-default'),
                ])
            ]),
    ]),
    html.Div(id='page-content', children=[])
])

@app.callback(
    [Output('json_event_log', 'data'),
     Output('graph-loading-output', 'children')],
    Input('dropdown-xes-select', 'value')
)
def set_global_variable(selected_filename):    
    if selected_filename is not None:
        current_file_path = Path(__file__).resolve().parent
        file_path = str(current_file_path / 'data' / (selected_filename + '.xes'))
        df_event_log = pm4py.read_xes(file_path)
        json_event_log = df_to_json(df_event_log)
        return json_event_log, None
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
        return resource_performance_analysis.layout
    else: # if redirected to unknown link
        return "Select a page to start analysing the XES file!"

# ROUTING-3: Change button style based on selected page
@app.callback(
    [Output({'type': 'dynamic-button', 'index': ALL}, 'className')],
    [Input({'type': 'dynamic-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'dynamic-button', 'index': ALL}, 'className')],
)
def update_button_classes(n_clicks, *args):
    ctx = dash.callback_context

    if not ctx.triggered:
        # No buttons have been clicked yet
        return dash.no_update

    button_id_triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    button_id_triggered = json.loads(button_id_triggered)

    button_states = ctx.states
    class_list = []

    for i in range(len(button_states)):
        key = {'type': 'dynamic-button', 'index': i+1}
        
        if key == button_id_triggered:
            class_list.append('button-default button-selected')
        else:
            class_list.append('button-default')

    return [class_list]

if __name__ == '__main__':
    app.run_server(debug=True)