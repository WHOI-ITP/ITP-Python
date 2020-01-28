import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime
import gsw.conversions as sw
from itp_python.filters import pre_filter_factory


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

    def depth(self):
        return -self.height()

    def height(self):
        return sw.z_from_p(self.pressure, self.latitude)

    def potential_temperature(self, p_ref=0):
        absolute_salinity = sw.SA_from_SP(self.salinity,
                                          self.pressure,
                                          self.longitude,
                                          self.latitude)
        return sw.pt_from_t(absolute_salinity,
                            self.temperature,
                            self.pressure,
                            p_ref)


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
        with sqlite3.connect(str(self.db_path.absolute())) as connection:
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
