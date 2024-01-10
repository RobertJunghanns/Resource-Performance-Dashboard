import pandas as pd

def activity_duration(event:pd.Series, activity_duration: pd.Timedelta):
    activity_duration_min = activity_duration.total_seconds() / 60
    return activity_duration_min