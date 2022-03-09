import pytest
from pathlib import Path
from itp.itp_query import ItpQuery


"""
These are functional tests on actual data. Verification data have
been manually extracted from source "itp final" files.
"""


@pytest.fixture
def connection():
    path = Path(__file__).parent / 'testdb.db'
    return ItpQuery(path)


def test_create_query_object(connection):
    assert connection.args == {}


def test_max_results(connection):
    connection.set_max_results(10)
    assert connection._max_results == 10


def test_set_filter_dict(connection):
    connection.set_filter_dict({'flying': 'squirrel'})


def test_set_filter_dict_wrong_type(connection):
    with pytest.raises(TypeError):
        connection.set_filter_dict(['flying', 'squirrel'])


def test_add_filter(connection):
    connection.add_filter('smurf', 'blue')
    assert connection.args == {'smurf': 'blue'}


def test_basic_query_validate_data(connection):
    args = {'system': [1]}
    connection.set_filter_dict(args)
    results = connection.fetch()
    # these values were verified by parsing itp1grd0001.dat by hand
    assert results[0].date_time == '2005-08-16T06:00:00'
    assert results[0].system_number == 1
    assert results[0].profile_number == 1
    assert results[0].latitude == pytest.approx(78.8267)
    assert results[0].longitude == pytest.approx(-150.1313)
    assert results[0].salinity == pytest.approx(
        [28.9558, 28.9696, 29.0048, 29.1166, 29.3397, 29.5717, 29.8253, 29.9834, 30.0896, 30.1587]
    )
    assert results[0].temperature == pytest.approx(
        [-1.4637, -1.4608, -1.4538, -1.4295, -1.3907, -1.3626, -1.3522, -1.3603, -1.3633, -1.3668]
    )
    assert results[0].pressure == pytest.approx(
        [9.7, 11.0, 12.0, 13.0, 14.0, 15.0, 16.1, 17.1, 18.1, 19.1]
    )


def test_query_unknown_argument(connection):
    args = {'purple': 'cow'}
    connection.set_filter_dict(args)
    with pytest.raises(ValueError):
        connection.fetch()


def test_query_too_many_results(connection):
    args = {'system': [1]}
    connection.set_max_results(5)
    connection.set_filter_dict(args)
    with pytest.raises(RuntimeError):
        connection.fetch()


def test_validate_extra_fields(connection):
    # the test database has 10 profiles with DO from itp100
    args = {'extra_variables': ['dissolved_oxygen']}
    connection.set_filter_dict(args)
    results = connection.fetch()
    assert len(results) == 10
    for r in results:
        assert r.system_number == 100


def test_validate_extra_fields_not_list(connection):
    args = {'extra_variables': 'dissolved_oxygen'}
    connection.set_filter_dict(args)
    with pytest.raises(ValueError):
        connection.fetch()


def test_validate_extra_fields_unknown_variable(connection):
    args = {'extra_variables': ['dissolved_oxygen', 'chipmunk']}
    connection.set_filter_dict(args)
    with pytest.raises(ValueError):
        connection.fetch()


def test_pressure_filter(connection):
    # Of the 60 profiles in the database, two profiles
    # itp4grd0003, itp4grd0004 didn't have pressure in the range
    # so should have been excluded from the results
    args = {'pressure': [0, 100]}
    connection.set_filter_dict(args)
    results = connection.fetch()
    assert len(results) == 58


def test_query_no_args(connection):
    results = connection.fetch()
    assert len(results) == 60
