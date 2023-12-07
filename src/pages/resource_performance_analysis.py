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
                    className='div-div-rp-sidebar',
                    children = [
                        html.P(
                            className='p-option-col',
                            children='Dropdown:', 
                        ),
                        dcc.Dropdown(
                            id='dropdown',
                            options=[]
                        ),
                ]),
                html.Div(
                    className='div-div-rp-sidebar',
                    children = [
                        html.P(
                            className='p-option-col',
                            children='Dropdown:', 
                        ),
                        dcc.Dropdown(
                            id='dropdown',
                            options=[]
                        ),
                ]),
            ]),
    ])
])