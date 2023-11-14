# package imports
import dash
from dash import html


# Register this page with the Dash application
dash.register_page(
    __name__,
    path='/',
    title='Resource Behavior Analysis'
)

# Define the page layout
layout = html.Div(
    [
        html.H3(children='RBA')
    ]
)