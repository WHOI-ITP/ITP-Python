from datetime import datetime, timedelta


def julian_to_iso8601(year, day, first_day=1):
    """
    Return an iso8601 time string from a year and day-of-year
    """
    date_time = datetime(year, 1, 1) + timedelta(day) - timedelta(first_day)
    return datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%S')
