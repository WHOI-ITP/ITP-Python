import pytest
from itp.filters import (
    SqlFilter,
    SystemFilter,
    LatitudeFilter,
    LongitudeFilter,
    DateTimeFilter,
    PressureFilter,
    ExtraVariableFilter,
    pre_filter_factory
)
from datetime import datetime


class DummyAbstractClass(SqlFilter):
    def __init__(self):
        pass


def test_abstract_class():
    dummy = DummyAbstractClass()
    with pytest.raises(NotImplementedError):
        dummy._check()
    with pytest.raises(NotImplementedError):
        dummy.value()


@pytest.mark.parametrize('name, klass', [
    ('system', SystemFilter),
    ('latitude', LatitudeFilter),
    ('longitude', LongitudeFilter),
    ('date_time', DateTimeFilter),
    ('extra_variables', ExtraVariableFilter)
])
def test_factory(name, klass):
    assert isinstance(
        pre_filter_factory(name, [1, 2]),
        klass
    )


def test_factory_pressure():
    assert pre_filter_factory('pressure', [1, 2, 3]) is None


def test_factory_unknown_type():
    with pytest.raises(ValueError):
        pre_filter_factory('DUMMY', [1, 2])


@pytest.mark.parametrize('klass', [
    LatitudeFilter,
    LongitudeFilter,
    DateTimeFilter,
    PressureFilter
])
def test_wrong_n_inputs(klass):
    with pytest.raises(ValueError):
        klass([1, 2, 3])


def test_sql_filter():
    with pytest.raises(NotImplementedError):
        SqlFilter(['DUMMY'])


def test_argument_not_list():
    with pytest.raises(ValueError):
        SystemFilter('DUMMY')


def test_system_filter_one_arg():
    args = [1]
    sql, return_args = SystemFilter(args).value()
    assert sql == '(system_number IN (?))'
    assert return_args == args


def test_system_filter_two_args():
    args = [1, 2]
    sql, return_args = SystemFilter(args).value()
    assert sql == '(system_number IN (?,?))'
    assert return_args == args


def test_latitude_filter_bad_range():
    with pytest.raises(ValueError):
        LatitudeFilter([-91, 45])
    with pytest.raises(ValueError):
        LatitudeFilter([45, 91])


def test_latitude_filter_wrong_order():
    with pytest.raises(ValueError):
        LatitudeFilter([85, 75])


def test_latitude_filter():
    args = [75, 85]
    sql, return_args = LatitudeFilter(args).value()
    assert sql == '(latitude >= ? AND latitude <= ?)'
    assert return_args == args


def test_longitude_filter_bad_range():
    with pytest.raises(ValueError):
        LongitudeFilter([-181, 45])
    with pytest.raises(ValueError):
        LongitudeFilter([45, 181])


def test_longitude_filter_and_or():
    args = [1, 2]
    sql, return_args = LongitudeFilter(args).value()
    assert sql == '(longitude > ? AND longitude < ?)'
    assert return_args == args

    args = [2, 1]
    sql, return_args = LongitudeFilter(args).value()
    assert sql == '(longitude > ? OR longitude < ?)'
    assert return_args == args

    args = [1, 1]
    sql, return_args = LongitudeFilter(args).value()
    assert sql == '(longitude > ? AND longitude < ?)'
    assert return_args == args


def test_date_time_filter_wrong_n_args():
    with pytest.raises(ValueError):
        DateTimeFilter([
            datetime.now(), datetime.now(), datetime.now()])


def test_date_time_filter_start_after_end():
    with pytest.raises(ValueError):
        DateTimeFilter([datetime.now(), datetime(1971, 1, 1)])


def test_date_time_filter():
    args = [datetime(1970, 1, 1), datetime(1971, 1, 1)]
    sql, return_args = DateTimeFilter(args).value()
    assert sql == '(date_time BETWEEN ? AND ?)'
    iso_times = [x.strftime('%Y-%m-%dT%H:%M:%S') for x in args]
    assert return_args == iso_times


def test_pressure_filter_top_lt_bottom():
    with pytest.raises(ValueError):
        PressureFilter([2, 1])


def test_pressure_filter():
    args = [1, 2]
    sql, return_args = PressureFilter(args).value()
    assert sql == '(pressure >= ? AND pressure <= ?)'
    assert return_args == pytest.approx([10000, 20000])


def test_extra_variable_filter():
    args = ['dissolved_oxygen', 'par']
    sql, return_args = ExtraVariableFilter(args).value()
    expected = 'profiles.id IN (SELECT profile_id FROM profile_extra_variables ' \
        'INNER JOIN variable_names ON profile_extra_variables.variable_id ' \
        '== variable_names.id WHERE variable_names.name IN ' \
        '(?,?))'
    assert sql == expected
    assert return_args == args
