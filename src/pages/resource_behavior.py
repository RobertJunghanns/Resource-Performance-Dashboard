from app import app
from dash import html, Input, Output, dcc
from model.xes_utility import get_unique_resources, json_to_df


layout = html.Div([
    html.Div(
        id='div-rbi-options',
        children = [
            html.Div(
                className='div-option-col',
                children = [
                    dcc.Dropdown(
                        id='dropdown-resource-select',
                        options=[]
                    )
                ],
            ),
            html.Div(
                className='div-option-col',
                children = [

                ],
            )
    ])
])

@app.callback(
    Output('dropdown-resource-select', 'options'),
    Input('json_event_log', 'data')
)
def update_resource_options(json_event_log):
    if json_event_log:
        df_event_log = json_to_df(json_event_log)
        unique_resources = get_unique_resources(df_event_log)
        sorted_resources = sorted(unique_resources)
        options = [{'label': resource, 'value': resource} for resource in sorted_resources]
        return options
    else:
        # Return an empty list if no file is selected
        return []