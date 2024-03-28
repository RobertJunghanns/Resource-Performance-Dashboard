# Resource Performance Analysis Dashbaord - A Framework Instantiation

## Requirements
The dashboard requires the following to run on **macOS**:

- Python 3.12.2 installed (e.g. with [Homebrew](https://brew.sh/#install) using [this guide](https://docs.python-guide.org/starting/install3/osx/))
- pipenv installed (e.g. using [Homebrew for pipenv](https://formulae.brew.sh/formula/pipenv))
- all other dependancies for the dashboard are specified in the `requirements.txt` and installed upon the first statup of the dashboard

## Run Dashboard
The following steps have do be performed to access and start the Dashboard. The project uses a `makefile` to wrap all important commands.

1. Clone project from GitHub
```
$ git clone https://github.com/RobertJunghanns/Resource-Performance-Dashboard.git
```
2. (Optional) Set the Dash application port and the XES attribute names in the `src/config.py` file.
3. Navigate to project folder.
```
$ cd project_folder_path
```
4. Create/enter pipenv shell.
```
$ make shell
```
5. Start the Dash application "Resource Performance Analysis Dashbaord" inside the shell. This implicitly installs all necessary dependancies if not already satisfied. Please note that the initial startup of the Dash application may take longer.
```
$ make run-dashboard
```
6. Open the Dash application.
```
$ open http://127.0.0.1:8050/
```
7. (Optional) Terminate the Dash application (CTRL + C) and exit the shell.
```
$ make exit
```

## Package Management
- Show all requirements of the application.
```
$ make show-requirements
```
- Update the requirements in the `requirements.txt` file.
```
$ make update-requirements
```
- Install all requirements of the `requirements.txt` file. This is implicitly done during the start of the application.
```
$ make install-requirements
```

## Tests
- Run all tests of the framework instance module.
```
$ make run-tests
```
- Run all tests of the framework instance module with statement and branch coverage.
```
$ make run-coverage-tests
```

## Example SQL queries for the use in the Dashboard
### Distinct Activities
```
SELECT COUNT(DISTINCT [concept:name])
        FROM event_log
        WHERE [org:resource] = '{r}'
```
### Activity Completions
```
SELECT COUNT([concept:name])
        FROM event_log
        WHERE [org:resource] = '{r}'
```
### Activity Frequency
```
SELECT CAST(count.activity AS FLOAT) / CAST(count.all_activities AS FLOAT)
FROM (
    SELECT
        (SELECT COUNT([concept:name])
         FROM event_log
         WHERE [org:resource] = '{r}'
         AND [concept:name] = '09_AH_I_010') AS activity,
        (SELECT COUNT([concept:name])
         FROM event_log
         WHERE [org:resource] = '{r}') AS all_activities
) AS count
```

### Custom: Average number of activities executed in a case by the participating resource
```
SELECT AVG(completed_activities) AS avg_completed_activities
FROM (
    SELECT [case:concept:name], 
           COUNT(*) AS completed_activities
    FROM event_log
    WHERE [lifecycle:transition] = 'complete'
    AND [org:resource] = '{r}'
    GROUP BY [case:concept:name]
) AS case_activities
```
### Custom: Average number of activities executed in a case where the resource participated
```
SELECT AVG(completed_activities) AS avg_completed_activities
FROM (
    SELECT e.[case:concept:name], 
           COUNT(*) AS completed_activities
    FROM event_log e
    INNER JOIN (
        SELECT DISTINCT [case:concept:name]
        FROM event_log
        WHERE [org:resource] = '{r}'
    ) r1_cases ON e.[case:concept:name] = r1_cases.[case:concept:name]
    WHERE e.[lifecycle:transition] = 'complete'
    GROUP BY e.[case:concept:name]
) AS completed_activities_per_case;
```
### Case Duration in Minutes
```
SELECT
    (CAST(strftime('%s', MAX([time:timestamp])) AS FLOAT) - 
     CAST(strftime('%s', MIN([time:timestamp])) AS FLOAT)) / 60
FROM
    trace
```

### Cost of application (case level) for BPIC'15
```
SELECT DISTINCT([case:SUMleges])
FROM trace
```

