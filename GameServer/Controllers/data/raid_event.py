import datetime
import math

RAID_EVENT_MAP_ID = 52
RAID_EVENT_NAME = 'Siege of the Dark Rift'
RAID_EVENT_ENABLED = True
RAID_OPEN_TIME = datetime.time(20, 0)
RAID_CLOSE_TIME = datetime.time(21, 0)


def _build_window(now):
    start = datetime.datetime.combine(now.date(), RAID_OPEN_TIME)
    end = datetime.datetime.combine(now.date(), RAID_CLOSE_TIME)
    if end <= start:
        end = start + datetime.timedelta(hours=1)
    if now >= end:
        start = start + datetime.timedelta(days=1)
        end = end + datetime.timedelta(days=1)
    return start, end


def get_next_raid_start_time(now=None):
    if not RAID_EVENT_ENABLED:
        return None
    current_time = now or datetime.datetime.now()
    start, _ = _build_window(current_time)
    return start


def is_raid_event_open(now=None):
    if not RAID_EVENT_ENABLED:
        return False
    current_time = now or datetime.datetime.now()
    start, end = _build_window(current_time)
    return start <= current_time <= end


def build_raid_event_message(_args, now=None, map_id=RAID_EVENT_MAP_ID):
    if not RAID_EVENT_ENABLED:
        return None
    current_time = now or datetime.datetime.now()
    start_time, end_time = _build_window(current_time)

    if current_time < start_time:
        minutes = max(0, math.ceil((start_time - current_time).total_seconds() / 60))
        return '[Raid] The raid "{0}" opens in {1} minute(s).'.format(RAID_EVENT_NAME, minutes), 3

    if start_time <= current_time <= end_time:
        remaining = max(0, math.ceil((end_time - current_time).total_seconds() / 60))
        if remaining <= 10:
            message = '[Raid] The raid "{0}" closes in {1} minute(s)!'.format(RAID_EVENT_NAME, remaining)
        else:
            message = '[Raid] The raid "{0}" is open! Closing in {1} minute(s).'.format(
                RAID_EVENT_NAME,
                remaining
            )
        return message, 3

    return None
