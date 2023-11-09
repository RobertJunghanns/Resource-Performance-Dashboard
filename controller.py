from  View.dashboard import Dashboard

class Controller():
    def __init__(self) -> None:
        self.dashboard = Dashboard()

if __name__ == '__main__':
    c = Controller()
    c.dashboard.app.run(debug=True)
    