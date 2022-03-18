import sqlite3
from pathlib import Path
from itp.filters import pre_filter_factory, PressureFilter
from itp.profile import Profile


class RawlocsQuery:
    def __init__(self, db_path, **kwargs):
        self.db_path = Path(db_path)
        self.args = kwargs
        self._max_results = 100000
        self._profiles = None

    def set_max_results(self, results):
        self._max_results = results

    def set_filter_dict(self, filter_dict):
        if type(filter_dict) is not dict:
            raise TypeError('filter_dict must be a dictionary')
        self.args = filter_dict

    def add_filter(self, param, value):
        self.args[param] = value

    def fetch(self):
        with sqlite3.connect(str(self.db_path.absolute())) as connection:
            cursor = connection.cursor()
            self._query_metadata(cursor)
        return self._profiles

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
        query = 'SELECT * FROM rawlocs'
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
        if query.endswith(' WHERE'):
            query = query[:-6]
        return query, sql_args

