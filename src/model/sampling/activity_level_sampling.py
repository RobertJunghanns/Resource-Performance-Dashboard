import pandas as pd
import numpy as np

from enum import Enum
from typing import Callable, List, Any
from model.utility.xes_utility import get_earliest_timestamp, get_latest_timestamp

class ScopeActivity(Enum):
    ACTIVITY = 1
    INDIVIDUAL = 2
    TOTAL = 3