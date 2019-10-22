import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime


class Profile:
    def __init__(self):
        self._id = None
        self.system_number = None
        self.profile_number = None
        self.date_time = None
        self.latitude = None
        self.longitude = None
        self.pressure = None
        self.salinity = None
        self.temperature = None
        self.source = None

    def python_datetime(self):
        return datetime.strptime(self.date_time, '%Y-%m-%dT%H:%M:%S')

    def posix_time(self):
        return self.python_datetime().timestamp()


class ItpQuery:
    def __init__(self, db_path, **kwargs):
        self.db_path = Path(db_path)
        self.params = kwargs
        self._max_results = 5000
        self._profiles = None

    def set_max_results(self, results):
        self._max_results = results

    def set_filter_dict(self, filter_dict):
        self.params = filter_dict

    def add_filter(self, param, value):
        self.params[param] = value

    def fetch(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            self._query_metadata(cursor)
            self._query_profiles(cursor)
        return self._profiles

    def _query_metadata(self, cursor):
        results = cursor.execute(self._build_query())
        fields = [x[0] for x in results.description]
        fields[0] = '_id'
        rows = results.fetchall()
        if len(rows) > self._max_results:
            error_str = '{} results exceed maximum of {}'
            raise RuntimeError(
                error_str.format(len(rows), self._max_results))
        self._profiles = []
        for row in rows:
            this_profile = Profile()
            for field, value in zip(fields, row):
                setattr(this_profile, field, value)
            self._profiles.append(this_profile)

    def _build_query(self):
        query = 'SELECT * FROM profiles'
        if self.params:
            query += ' WHERE'
        for parameter, values in self.params.items():
            sql_filter = pre_filter_factory(parameter, values)
            if sql_filter:
                query += ' ' + sql_filter.value() + ' AND'
        if query.endswith(' AND'):
            query = query[:-4]
        query += ' ORDER BY system_number, profile_number'
        return query

    def _query_profiles(self, cursor):
        for profile in self._profiles:
            profile_id = profile._id
            fields = ['pressure', 'temperature', 'salinity']
            format_str = '{0}/10000.0 as {0}'
            query = 'SELECT '
            query += ', '.join([format_str.format(x) for x in fields])
            query += ' FROM ctd'
            query += ' WHERE profile_id = {} ORDER BY pressure'.format(
                profile_id)
            results = cursor.execute(query)
            values = np.array(results.fetchall())
            for i, field in enumerate(fields):
                setattr(profile, field, values[:, i])


def pre_filter_factory(parameter, values):
    parameter_classes = {
        'system': SystemFilter,
        'latitude': LatitudeFilter,
        'longitude': LongitudeFilter,
        'date_time': DateTimeFilter
    }
    if parameter not in parameter_classes.keys():
        raise ValueError('Unknown filter {}'.format(parameter))
    return parameter_classes[parameter](values)


class SqlFilter:
    def __init__(self, params):
        self.params = params
        self._check()

    def _check(self):
        raise NotImplementedError

    def value(self):
        raise NotImplementedError


class SystemFilter(SqlFilter):
    def _check(self):
        if type(self.params) != list:
            raise ValueError('Systems values must be a list')

    def value(self):
        system_query = '('
        for system in self.params:
            system_query += 'system_number={} OR '.format(system)
        return system_query[:-3] + ')'


class LatitudeFilter(SqlFilter):
    def _check(self):
        for value in self.params:
            if value < -90 or value > 90:
                raise ValueError('Latitude must be in range -90 to 90')
        if self.params[0] >= self.params[1]:
            raise ValueError('Latitude values must be increasing')

    def value(self):
        lat_format = '(latitude >= {} AND latitude <= {})'
        return lat_format.format(*self.params)


class LongitudeFilter(SqlFilter):
    def _check(self):
        for value in self.params:
            if value < -180 or value > 180:
                raise ValueError('Longitude must be in range -180 to 180')

    def value(self):
        lon_format = '(longitude > {0} {2} longitude < {1})'
        lon = self.params
        logical = 'OR' if lon[1] < lon[0] else 'AND'
        return lon_format.format(*lon, logical)


class DateTimeFilter(SqlFilter):
    def _check(self):
        if self.params[0] > self.params[1]:
            raise ValueError('End time must be after start time')

    def value(self):
        format_str = '(date_time BETWEEN "{}" AND "{}")'
        iso_times = [x.strftime('%Y-%m-%dT%H:%M:%S') for x in self.params]
        return format_str.format(*iso_times)
