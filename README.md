# Artefakt

## Commands
### Run Dashboard the First Time
- Navigate to project folder
- Go in shell: pipenv shell
- Install listed requirements recursivly: pip install -r requirements.txt
- Start Dashboard: python src/index.py 
- Open in Browser: http://127.0.0.1:8050/
- Exit out of shell: exit
### Package Management
Show packages: pip freeze
Create requirements.txt: pip freeze > requirements.txt
### Tests
Run tests from root: python -m unittest discover -s tests
Run statement coverage test: coverage run --source=src/model -m unittest discover -s tests
Run statment and branch coverage test: coverage run --branch --source=src/model -m unittest discover -s tests
Get coverage report: coverage report
Get html coverage report: coverage html
Open html coverage report: open htmlcov/index.html


## TODO's
- global variables (HOSTID)


