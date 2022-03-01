import sqlite3
import numpy as np
from pathlib import Path
from itp.filters import pre_filter_factory, PressureFilter
from itp.profile import Profile


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

            # make sure any "extra_variables" are valid
            self._check_extra_fields(cursor)

            # build up the profiles
            self._query_metadata(cursor)
            self._query_profiles(cursor)
            self._remove_empty_profiles()
        return self._profiles

    def _check_extra_fields(self, cursor):
        if 'extra_variables' not in self.args:
            return
        sql = 'SELECT name FROM variable_names'
        known_extra_vars = cursor.execute(sql).fetchall()
        known_extra_vars = [f[0] for f in known_extra_vars]
        for var in self.args['extra_variables']:
            if var not in known_extra_vars:
                raise ValueError(f'Unknown extra_variable {format(var)}')

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
            sql_args = [profile._id]
            fields = ['pressure', 'temperature', 'salinity']
            format_str = '{0}/10000.0 as {0}'
            query = 'SELECT '
            query += ', '.join([format_str.format(x) for x in fields])
            query += ' FROM ctd'
            query += ' WHERE profile_id = ?'
            if 'pressure' in self.args:
                sql, args = PressureFilter(self.args['pressure']).value()
                query += ' AND ' + sql
                sql_args.extend(args)
            query += ' ORDER BY pressure'
            results = cursor.execute(query, sql_args)

            values = np.array(results.fetchall(), dtype=np.float)
            if values.size == 0:
                # the pressure filter may eliminate all the samples
                # in that case, remove the profile
                continue
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

    def _remove_empty_profiles(self):
        self._profiles = [p for p in self._profiles if p.pressure is not None]
