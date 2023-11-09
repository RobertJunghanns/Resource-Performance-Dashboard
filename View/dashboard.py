from dash import Dash, html

class Dashboard():
   #create Model based on XES-File provided by View
    def __init__(self) -> None:
        self.app = self.createDashboard()

    def createDashboard(self):
        app = Dash()
        app.layout = html.Div([
            html.Div(children='Hello World')
        ])
        return app
    
    def runDashboard(self):
        self.app.run(debug=True)

    
    