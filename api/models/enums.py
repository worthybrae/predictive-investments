# api/models/enums.py
from enum import Enum

class Timespan(str, Enum):
    """Timespan options for stock data aggregation."""
    minute = "minute"
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"
    quarter = "quarter"
    year = "year"

class SortOrder(str, Enum):
    """Sort order options."""
    asc = "asc"
    desc = "desc"