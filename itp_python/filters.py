

def pre_filter_factory(parameter, values):
    parameter_classes = {
        'system': SystemFilter,
        'latitude': LatitudeFilter,
        'longitude': LongitudeFilter,
        'date_time': DateTimeFilter,
        'extra_variables': ExtraVariableFilter
    }
    # pressure is the only post filter so we can simply check for it here
    # so it doesn't throw an unknown filter error
    if parameter == 'pressure':
        return None
    if parameter not in parameter_classes.keys():
        raise ValueError('Unknown filter {}'.format(parameter))
    return parameter_classes[parameter](values)


class SqlFilter:
    def __init__(self, args):
        self.args = args
        self._check_list()
        self._check()

    def _check_list(self):
        if type(self.args) != list:
            raise ValueError('All arguments must be a list.')


    def _check(self):
        raise NotImplementedError

    def value(self):
        # returns a two element tuple. The first value is the sql portion
        # with ? for variables. The second value is a list of values to
        # be inserted where the ? occurs in the sql.
        raise NotImplementedError


class SystemFilter(SqlFilter):
    def _check(self):
        pass

    def value(self):
        sql = '(system_number IN (' + ','.join('?' * len(self.args)) + '))'
        return sql, self.args


class LatitudeFilter(SqlFilter):
    def _check(self):
        if len(self.args) != 2:
            raise ValueError('Latitude must contain exactly two values.')
        for value in self.args:
            if value < -90 or value > 90:
                raise ValueError('Latitude must be in range -90 to 90')
        if self.args[0] >= self.args[1]:
            raise ValueError('Latitude values must be increasing')

    def value(self):
        sql = '(latitude >= ? AND latitude <= ?)'
        return sql, self.args


class LongitudeFilter(SqlFilter):
    def _check(self):
        if len(self.args) != 2:
            raise ValueError('Longitude must contain exactly two values.')
        for value in self.args:
            if value < -180 or value > 180:
                raise ValueError('Longitude must be in range -180 to 180')

    def value(self):
        logical = 'OR' if self.args[1] < self.args[0] else 'AND'
        sql = f'(longitude > ? {logical} longitude < ?)'
        return sql, self.args


class DateTimeFilter(SqlFilter):
    def _check(self):
        if len(self.args) != 2:
            raise ValueError('Datetime must contain exactly two values.')
        if self.args[0] > self.args[1]:
            raise ValueError('End time must be after start time')

    def value(self):
        sql = '(date_time BETWEEN ? AND ?)'
        iso_times = [x.strftime('%Y-%m-%dT%H:%M:%S') for x in self.args]
        return sql, iso_times


class PressureFilter(SqlFilter):
    def _check(self):
        if len(self.args) != 2:
            raise ValueError('Pressure range must contain exactly two values.')
        if self.args[0] > self.args[1]:
            raise ValueError('Top pressure must be less than bottom pressure')

    def value(self):
        sql = '(pressure >= ? AND pressure <= ?)'
        pressures = [self.args[0] * 10000.0, self.args[1] * 10000.0]
        return sql, pressures



class ExtraVariableFilter(SqlFilter):
    def _check(self):
        pass

    def value(self):
        sql = 'profiles.id IN '
        sql += '(SELECT profile_id FROM profile_extra_variables '
        sql += 'INNER JOIN variable_names '
        sql += 'ON profile_extra_variables.variable_id == variable_names.id '
        sql += 'WHERE variable_names.name IN '
        sql += '(' + ','.join('?' * len(self.args)) + '))'
        return sql, self.args

