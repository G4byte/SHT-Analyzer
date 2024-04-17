import pandas as pd
import numpy as np
from datetime import datetime as dt 
from datetime import timedelta
from itertools import chain



def standardize_datetime(csv_filepath):
# Read SHT csv log and ensure no funky time format survives
    df = pd.read_csv(csv_filepath)
    df["date-time"] = pd.to_datetime(df["date-time"], format = "%Y/%m/%d %H:%M:%S")
    return df
    
def fit_format(fit_retval):
# Helper function to format output of warming fit (units / second)
    return np.array((fit_retval[0], np.sqrt(np.diag(fit_retval[1])))) 

def measure_time(unit_alias, time_string):
# Returns the quantity of some unit of time from a colloquial string
# e.g. with "12 h" or "12 hours" returns 12.0
    time_string = time_string.split()
    if unit_alias not in time_string:
        return 0.
    return float(time_string[time_string.index(unit_alias) - 1])
    
def timedelta_from_duration(dur):
# Converts colloquial input of days, hours, minutes to a usable timedelta object

    dur = dur.lower()
    dhm = [0.,0.,0.]
    # Prefer float addition from the outset rather than add float and int

    alias_list = [["d","h","m"], ["days", "hours", "minutes"]]

    for i, alias in enumerate(alias_list[0]):
        dhm[i] += measure_time(alias, dur)
    for i, alias in enumerate(alias_list[1]):
        if dhm[i] == 0.:
            dhm[i] += measure_time(alias, dur)

    return timedelta(days = dhm[0], hours = dhm[1], minutes = dhm[2])