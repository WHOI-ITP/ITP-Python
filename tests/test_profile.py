import pytest
from itp.profile import Profile
from datetime import datetime


"""
gsw validations were done using MATLAB TEOS-10 toolbox
"""


@pytest.fixture
def profile():
    p = Profile()
    p.date_time = '1970-01-01T00:00:00'
    p.latitude = 80
    p.longitude = 0
    p.pressure = [0, 1, 2, 3, 4, 5]
    p.salinity = [20, 24, 28, 32, 36, 40]
    p.temperature = [0, 1, 2, 3, 4, 5]
    return p


def test_python_datetime(profile):
    epoc = datetime(1970, 1, 1)
    assert profile.python_datetime() == epoc


def test_posix_time(profile):
    assert profile.posix_time() == 0


def test_absolute_salinity(profile):
    abs_salinity = profile.absolute_salinity()
    expected = [20.0956, 24.1147, 28.1338, 32.1529, 36.1721, 40.1912]
    assert abs_salinity == pytest.approx(expected, abs=1e-4)


def test_height(profile):
    height = profile.height()
    expected = [0, -0.9894, -1.9788, -2.9682, -3.9576, -4.9470]
    assert height == pytest.approx(expected, abs=1e-4)


def test_depth(profile):
    depth = profile.depth()
    expected = [0, 0.9894, 1.9788, 2.9682, 3.9576, 4.9470]
    assert depth == pytest.approx(expected, abs=1e-4)


def test_conservative_temp(profile):
    conservative_temp = profile.conservative_temperature()
    expected = [0.0399, 1.0500, 2.0435, 3.0214, 3.9842, 4.9327]
    assert conservative_temp == pytest.approx(expected, abs=1e-4)


def test_density(profile):
    density = profile.density()
    expected = [1016.0, 1019.2, 1022.4, 1025.5, 1028.6, 1031.7]
    assert density == pytest.approx(expected, abs=1e-1)


def test_p_temp(profile):
    p_temp = profile.potential_temperature()
    expected = [0, 1.0000, 1.9999, 2.9998, 3.9997, 4.9996]
    assert p_temp == pytest.approx(expected, abs=1e-4)


def test_freeze_temp(profile):
    freeze = profile.freezing_temperature_zero_pressure()
    expected = [-1.0667, -1.2889, -1.5145, -1.7439, -1.9773, -2.2147]
    assert freeze == pytest.approx(expected, abs=1e-4)


def test_heat_capacity(profile):
    heat_cap = profile.heat_capacity()
    expected = [4080.2, 4053.5, 4028.2, 4004.2, 3981.4, 3959.6]
    assert heat_cap == pytest.approx(expected, abs=1e-1)
