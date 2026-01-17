import datetime

# Configure event windows by date ranges (month/day).
# Add multiple ranges as needed; ranges can cross months.
WEEKEND_EVENT_WINDOWS = [
    ((12, 7), (12, 8)),
]

CHRISTMAS_EVENT_WINDOWS = [
    ((12, 1), (12, 7)),
]


def _date_in_windows(today, windows):
    for start, end in windows:
        start_date = datetime.date(today.year, start[0], start[1])
        end_date = datetime.date(today.year, end[0], end[1])
        if end_date < start_date:
            end_date = datetime.date(today.year + 1, end[0], end[1])
        if start_date <= today <= end_date:
            return True
    return False


def is_weekend_event_active(now: datetime.datetime = None):
    """Return whether the weekend experience event is active."""
    current = now or datetime.datetime.now()
    return _date_in_windows(current.date(), WEEKEND_EVENT_WINDOWS)


def is_christmas_event_active(now: datetime.datetime = None):
    """Return whether the Christmas event is active."""
    current = now or datetime.datetime.now()
    return _date_in_windows(current.date(), CHRISTMAS_EVENT_WINDOWS)
