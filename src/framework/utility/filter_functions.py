import config
import pm4py

# filter all direct declined cases in BPIC'12 when sub-sampling case ids
def filter_direct_decline_bpic_12(event_log):
    event_log = pm4py.filter_variants(event_log, [('A_SUBMITTED','A_PARTLYSUBMITTED', 'A_DECLINED')], retain=False, activity_key=config.activity_col, case_id_key=config.case_col, timestamp_key=config.timestamp_col)
    return event_log

# filter all canceled and declined cases in BPIC'12 when sub-sampling case ids
def filter_cancel_decline_bpic_12(event_log):
    event_log = pm4py.filter_event_attribute_values(event_log, config.activity_col, ["A_DECLINED", "A_CANCELLED"], level="case", retain=False)
    return event_log