

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
