import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime
import gsw
from itp_python.filters import pre_filter_factory, ExtraVariableJoin


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
        return gsw.conversions.z_from_p(self.pressure, self.latitude)

    def absolute_salinity(self):
        return gsw.conversions.SA_from_SP(
            self.salinity,
            self.pressure,
            self.longitude,
            self.latitude
        )

    def conservative_temperature(self):
        return gsw.conversions.CT_from_t(
            self.absolute_salinity(),
            self.temperature,
            self.pressure
        )

    def density(self):
        return gsw.density.rho(
            self.absolute_salinity(),
            self.conservative_temperature(),
            self.pressure
        )

    def potential_temperature(self, p_ref=0):
        return gsw.conversions.pt_from_t(
            self.absolute_salinity(),
            self.temperature,
            self.pressure,
            p_ref
        )

    def freezing_temperature_zero_pressure(self):
        return gsw.CT_freezing(
            self.absolute_salinity(),
            p=0,
            saturation_fraction=1
        )

    def heat_capacity(self):
        return gsw.cp_t_exact(
            self.absolute_salinity(),
            self.temperature,
            self.pressure
        )


class ItpQuery:
    def __init__(self, db_path, **kwargs):
        self.db_path = Path(db_path)
        self.args = kwargs
        self._max_results = 5000
        self._profiles = None

    def set_max_results(self, results):
        self._max_results = results

    def set_filter_dict(self, filter_dict):
        self.args = filter_dict

    def add_filter(self, param, value):
        self.args[param] = value

    def fetch(self):
        with sqlite3.connect(str(self.db_path.absolute())) as connection:
            cursor = connection.cursor()
            self._check_extra_fields(cursor)
            self._query_metadata(cursor)
            self._query_profiles(cursor)
        return self._profiles

    def _check_extra_fields(self, cursor):
        if 'extra_variables' not in self.args:
            return
        sql = 'SELECT name FROM variable_names'
        known_extra_vars = cursor.execute(sql).fetchall()
        known_extra_vars = [f[0] for f in known_extra_vars]
        for var in self.args['extra_variables']:
            if var not in known_extra_vars:
                raise ValueError('Unknown extra_variable {}'.format(var))

    def _query_metadata(self, cursor):
        results = cursor.execute(*self._build_query())
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
        sql_args = []
        if self.args:
            query += ' WHERE'
        for argument, values in self.args.items():
            sql_filter = pre_filter_factory(argument, values)
            if sql_filter:
                sql, these_args = sql_filter.value()
                query += ' ' + sql + ' AND'
                sql_args.extend(these_args)
        if query.endswith(' AND'):
            query = query[:-4]
        query += ' ORDER BY system_number, profile_number'
        return query, sql_args

    def _query_profiles(self, cursor):
        for profile in self._profiles:
            profile_id = profile._id
            fields = ['pressure', 'temperature', 'salinity']
            # for variable in self.args['extra_variables']:
            #     fields.append(variable)
            format_str = '{0}/10000.0 as {0}'
            sql = 'SELECT '
            sql += ', '.join([format_str.format(x) for x in fields])
            sql += ' FROM ctd'
            sql += ' WHERE profile_id = {} ORDER BY pressure'.format(
                profile_id)
            results = cursor.execute(sql)
            values = np.array(results.fetchall(), dtype=np.float)
            for i, field in enumerate(fields):
                setattr(profile, field, values[:, i])
            if 'extra_variables' in self.args:
                self._load_extra_variables(cursor, profile)

    def _load_extra_variables(self, cursor, profile):
        for var in self.args['extra_variables']:
            sql = 'SELECT value/10000.0 val FROM ctd '
            sql += 'LEFT JOIN other_variables '
            sql += 'ON ctd.id == other_variables.ctd_id AND variable_id == '
            sql += '(SELECT id FROM variable_names WHERE name == ?) '
            sql += 'WHERE ctd.profile_id == ?'
            sql += 'ORDER BY pressure'
            results = cursor.execute(sql, [var, profile._id])
            values = np.array(results.fetchall(), dtype=np.float)
            setattr(profile, var, values[:, 0])
