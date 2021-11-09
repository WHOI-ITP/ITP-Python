from admin_tools.utils import julian_to_iso8601


def test_first_day_of_year():
    assert julian_to_iso8601(2019, 1) == '2019-01-01T00:00:00'


def test_last_day_of_year():
    assert julian_to_iso8601(2019, 365) == '2019-12-31T00:00:00'


def test_leap_year():
    assert julian_to_iso8601(2016, 60) == '2016-02-29T00:00:00'


def test_last_day_of_year_w_leap_year():
    assert julian_to_iso8601(2016, 366) == '2016-12-31T00:00:00'


def test_fractional_day():
    assert julian_to_iso8601(2019, 1.75) == '2019-01-01T18:00:00'


def test_zero_start_day():
    assert julian_to_iso8601(2019, 0, first_day=0) == '2019-01-01T00:00:00'
