import dash_bootstrap_components as dbc
from dash import Dash

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], )
app.config.suppress_callback_exceptions = True



