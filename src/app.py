# package imports
import base64
import uuid
import dash_bootstrap_components as dbc
import dash
from dash import Dash, html, dcc, callback, Input, Output, State, page_registry
from pathlib import Path

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], )

from pages import resource_behavior, resource_performance_analysis

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
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
                className='div-in-optin-box',
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
                                options=[],
                                value='UF'
                            ),
                    ]),
            ]),
    ]),
    html.Div(
        className='div-option-box',
        children=[
            html.Div(
                className='div-in-optin-box',
                children = [
                html.P(id='p-page-select', children='Select page'),
                html.Div(
                    id='div-buttons',
                    children=[
                        html.Button('Resource Behavior', id='button-resource-behavior', className='button-default'),
                        html.Button('Resource-Performance Analysis', id= 'button-resource-performance-analysis', className='button-default')
                ])
            ]),
    ]),
    html.Div(id='page-content', children=[])
])

# Define the callback for the upload component
@callback(
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

# Set url based on selected page
@app.callback(
    Output('url', 'pathname'),
    [Input('button-resource-behavior', 'n_clicks'),
     Input('button-resource-performance-analysis', 'n_clicks')],
)
def navigate(n_clicks_behaviour, n_clicks_performance):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'button-resource-behavior':
        return '/resource-behavior'
    elif button_id == 'button-resource-performance-analysis':
        return '/resource-performance-analysis'
    else:
        return dash.no_update
    
# Supply page-content based on url
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/resource-behavior':
        return resource_behavior.layout
    if pathname == '/resource-performance-analysis':
        return resource_performance_analysis.layout
    else: # if redirected to unknown link
        return "404 Page Error! Please choose a link"

if __name__ == '__main__':
    app.run_server(debug=True)

