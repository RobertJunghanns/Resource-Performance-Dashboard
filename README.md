# Resource-Performance Analysis Dashbaord - A Framework Instantiation

## Commands
### Run Dashboard
The following steps have do be performed to start and access the Dashboard. The project folder uses a makefile to wrap all commands.
- Navigate to project folder
- Go in shell: make shell
- Start Dashboard: make run-dashboard
- Open Browser: http://127.0.0.1:8050/
- Exit out of shell: make exit
### Package Management
Show requirements: make show-requirements
Update requirements.txt: make update-requirements
Install requirements (implicit by run-dashboard): make install-requirements
### Tests
Run tests: make run-tests
Run tests with statement and branch coverage: make run-tests

## Example SQL queries
### Custom RBI: Example SQL queries:
#### Distinct Activities
SELECT COUNT(DISTINCT [concept:name])
        FROM event_log
        WHERE [org:resource] = '{r}'
#### Activity Completions
SELECT COUNT([concept:name])
        FROM event_log
        WHERE [org:resource] = '{r}'
#### Activity Frequency
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
### Custom Performance Metric: Example SQL query:
SELECT
    (CAST(strftime('%s', MAX([time:timestamp])) AS FLOAT) - 
     CAST(strftime('%s', MIN([time:timestamp])) AS FLOAT)) / 60
FROM
    trace

