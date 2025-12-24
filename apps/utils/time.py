from time import gmtime, strftime

import pytz


UTC_TIMEZONE = pytz.utc


def duration_to_str(seconds):
    if seconds is None:
        return
    _format = ('%H:%M:%S' if seconds >= 3600  # 1 hour
               else '%M:%S')
    return strftime(_format, gmtime(seconds))


def datetime_to_tz(dt, tz):
    if dt:
        dt = dt.astimezone(tz)
    return dt


def datetime_to_utc(dt):
    return datetime_to_tz(dt, tz=UTC_TIMEZONE)
