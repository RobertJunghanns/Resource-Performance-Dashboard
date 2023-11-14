# package imports
import dash
import base64
import os
from dash import html, dcc, callback, Input, Output, State
from pathlib import Path


# Register this page with the Dash application
dash.register_page(
    __name__,
    path='/home',
    title='Upload XES File'
)

# Define the page layout
layout = html.Div(
    [
        html.H1('Upload XES Files'),
        dcc.Upload(
            id='upload-xes',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow only .xes files
            accept='.xes',
            multiple=False
        ),
        html.Div(id='output-upload')
    ]
)

# Define the callback for the upload component
@callback(
    Output('output-upload', 'children'),
    Input('upload-xes', 'contents'),
    State('upload-xes', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        _, content_string = contents.split(',')
        if filename.endswith('.xes'):
            # Get the absolute path for the current script (upload.py)
            current_file_path = Path(__file__).resolve()

            # Get the src directory path by going up two levels from the current file
            src_dir_path = current_file_path.parents[1]

            # Define the data directory path
            data_dir_path = src_dir_path / 'data'

            # Create the data directory if it doesn't exist
            data_dir_path.mkdir(parents=True, exist_ok=True)

            # Define the save_path using the data directory path
            save_path = data_dir_path / filename
            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(content_string))
            return html.Div([
                'File uploaded successfully: {}'.format(filename)
            ])
        else:
            return html.Div([
                'This file type is not supported. Please upload a .xes file.'
            ])