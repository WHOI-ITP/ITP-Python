from itp_python.itp_final import parse_itp_final
import os
import pytest


def file(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'data', filename)


@pytest.fixture
def small_data_file():
    return parse_itp_final(file('itp1grd0001.dat'))


def test_read_metadata(small_data_file):
    expected_metadata = {
        'source': 'itp1grd0001.dat',
        'system_number': 1,
        'profile_number': 1,
        'date_time': '2005-08-16T06:00:00',
        'latitude': 78.8267,
        'longitude': -150.1313,
        'variables': ['pressure', 'temperature', 'salinity', 'nobs']}

    for key in expected_metadata:
        assert small_data_file.metadata(key) == expected_metadata[key]


def test_read_data(small_data_file):
    expected_data = {
        'pressure': [9.7, 11.0, 12.0, 13.0, 14.0, 15.0, 16.1],
        'temperature': [-1.4637, -1.4608, -1.4538, -1.4295,
                        -1.3907, -1.3626, -1.3522],
        'salinity': [28.9558, 28.9696, 29.0048, 29.1166,
                     29.3397, 29.5717, 29.8253],
        'nobs': [34.0, 4.0, 4.0, 4.0, 4.0, 5.0, 4.0]}
    for key in expected_data:
        assert small_data_file.data(key) == expected_data[key]


def test_read_scaled_data(small_data_file):
    data = small_data_file.scaled_data('pressure')
    pass

def test_variables(small_data_file):
    assert small_data_file.variables() == \
           ['pressure', 'temperature', 'salinity', 'nobs']
