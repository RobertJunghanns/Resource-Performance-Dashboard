# package imports
import base64
import dash_bootstrap_components as dbc
import dash
from dash import Dash, html, dcc, callback, Input, Output, State, page_registry
from pathlib import Path


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

# Get the list of page names and their paths from the page_registry
pages_info = [{'name': page['name'], 'path': page['path']} for page in page_registry.values()]

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(
        children=[
            html.A(
                html.Div(
                    children=html.Img(
                        src="./assets/dashboard.png",
                        style={"display": "inline-block", "float": "left", "height": "45px",
                               "padding": "-6px", "margin-top": "5px", "margin-left": "10px"}
                    ),
                ),
                href="https://opendatabim.com/#", target="_blank",
            ),
            html.H2(
                children="Resource-Performance Analysis for Event Logs", 
                style={'margin-left': '45px',  'margin-top': '13px', 'font-family': 'Arial',  'display': 'inline-block', 'font-weight': '500',  'font-size': '25px'}
            ),
            html.A(
                id='gh-link',
                children=[
                    'View on GitHub'
                ],
                href="https://github.com/RobertJunghanns/Resource-Performance-Dashboard",
                style={'color': 'white',
                       'border': 'solid 1px white',
                       'text-decoration': 'none',
                       'font-size': '10pt',
                       'font-family': 'sans-serif',
                       'color': '#fff',
                       'border': 'solid 1px #fff',
                       'border-radius': '2px',
                                        'padding': '2px',
                                        'padding-top': '5px',
                                        'padding-left': '15px',
                                        'padding-right': '15px',
                                        'font-weight': '100',
                                        'position': 'relative',
                                        'top': '15px',
                                        'float': 'right',
                                        'margin-right': '40px',
                                        'margin-left': '5px',
                                        'transition-duration': '400ms',
                       }
            ),
            html.Div(
                className="div-logo",
                children=html.Img(
                    className="logo", src=("./assets/github.png"),
                    style={'height': '48px',
                           'padding': '6px', 'margin-top': '3px'}
                ), 
                style={'display': 'inline-block', 'float': 'right'}
            ),
        ], style={"background": "#2c5c97", "color": "white", "padding-top": "15px", "padding-left": "48px", "padding-bottom": "25px", "padding-left": "24px"}
    ),
    dbc.Alert(id='upload-alert', duration=4000, dismissable=True, is_open=False),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.P(children='Upload XES file', style={
                            'margin-left':  '10px', }),
                        dcc.Upload(
                            id='upload-xes',
                            children=html.Div([
                                '📥 Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '40px',
                                'lineHeight': '40px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            # Allow multiple files to be uploaded
                            multiple=False
                        ),
                    ]),
                ], style={'width': '55%', 'display': 'inline-block'}),
                html.Div([
                    html.P(children='Select XES file', style={
                        'margin-left':  '2px', 'padding-top':  '-100px', }),
                    dcc.Dropdown(
                        id='xes-dropdown',
                        options=[],
                        value='UF',
                        style={'height': '40px',
                                'width': '250px',
                                'margin-top':  '7px',
                                'margin-bottom':  '20px',
                                'font-size': '16px'}
                    ),
                ], style={'width': '45%',  'display': 'inline-block', "padding-left": "30px", 'vertical-align': 'top', "padding-top": "0px"}),
            ], style={'width': '100%',   'display': 'inline-block', 'background': 'rgb(233 238 246)',
                        'border': '2px', 'border-radius': '10px', }),
        ], style={'width': '95%', 'display': 'inline-block', "margin-top": "10px", }),

    ], style={'width': '49%', 'background': 'rgb(233 238 246)', "margin-top": "10px", "margin-left": "10px",
                "padding-left": "40px", "padding-right": "40px", "padding-top": "10px", "padding-bottom": "10px", 'border': '2px', 'border-radius': '10px', 'display': 'inline-block'}),
    html.Div([
        html.Div([
            html.P(children='Select page', style={'margin-left':  '10px', }),
            html.Div(
                [html.Button(page['name'], id={'type': 'nav-button', 'index': page['path']}, n_clicks=0, style={
                    'background-color': 'white',
                    'border': '1px solid #ccc',
                    'border-radius': '4px',
                    'padding': '10px 15px',
                    'margin-right': '5px',
                    'font-size': '16px',
                    'text-align': 'center',
                    'cursor': 'pointer',
                    'line-height': '1.5'})
                for page in pages_info]
            )
        ], style={'width': '95%', 'display': 'inline-block', "margin-top": "10px", }),
    ], style={'width': '49%', 'background': 'rgb(233 238 246)', "margin-top": "10px", "margin-left": "10px",
                "padding-left": "40px", "padding-right": "40px", "padding-top": "10px", "padding-bottom": "10px", 'border': '2px', 'border-radius': '10px', 'display': 'inline-block'}),
    #dcc.Store(id='selected_XES_file_name'),
    dash.page_container
])

# Define the callback for the upload component
@callback(
    [Output('upload-alert', 'children'),
    Output('upload-alert', 'color'),
    Output('upload-alert', 'is_open'),
    Output('xes-dropdown', 'options')],
    [Input('upload-xes', 'contents')],
    [State('upload-xes', 'filename')]
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

# Callback to update the style of the buttons to reflect which page is currently displayed
@app.callback(
    Output({'type': 'nav-button', 'index': dash.ALL}, 'style'),
    Input('url', 'pathname')
)
def highlight_active_button(pathname):
    # Create the default style for all buttons
    default_style = {'margin-right': '5px', 'border': '1px solid black'}

    # Create a highlighted style for the active button
    active_style = {'margin-right': '5px', 'border': '3px solid black', 'font-weight': 'bold'}

    # Update the style for the active button based on the current pathname
    return [active_style if page['path'] == pathname else default_style for page in pages_info]    

if __name__ == '__main__':
    app.run(debug=True)