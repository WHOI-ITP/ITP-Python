from datetime import datetime, timedelta
from itp_python.itp import ItpProfile
from pathlib import Path
import logging


logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y/%m/%dT%I:%M:%S',
                    filename='example.log',
                    filemode='w',
                    level=logging.DEBUG)

MISSING_VALUE = '---0---'


class WODCollection:
    def __init__(self, parent_directory):
        self.parent_directory = parent_directory
        self.paths = list(Path(parent_directory).glob('**/*.CTD*.csv'))

    def next(self, f):
        data = []
        line = f.readline()
        while not line.startswith('CAST'):
            if line == '':
                return None
            line = f.readline()
        while not line.startswith('END OF VARIABLES') :
            data.append(line)
            line = f.readline()
        return data

    def __iter__(self):
        for path in self.paths:
            with open(path, 'r') as f:
                while True:
                    data = self.next(f)
                    if not data:
                        break
                    try:
                        yield WODParser(data).parse()
                    except ValueError:
                        yield None
                    except TypeError:
                        logging.exception('Exception caught during parsing')


class WODParser:
    def __init__(self, data):
        self.data = [[x.strip() for x in line.split(',')] for line in data]
        self.metadata = dict()
        self.metadata['source'] = 'WOD data'
        self.variables = {'temperature': list(),
                          'pressure': list(),
                          'salinity': list()}

    def parse(self):
        self.parse_header()
        self.read_data()
        return ItpProfile(self.metadata, self.variables)

    def parse_header(self):
        m = self.metadata
        header = self.data[:self._find_tag('VARIABLES', self.data)]
        m['date_time'] = self._parse_time(header)
        m['latitude'], m['longitude'] = self._parse_lat_lon(header)
        m['profile_number'] = self._header_vals('CAST', header)[0]
        m['system_number'] = self._header_vals('NODC Cruise ID', header)[0]

    def read_data(self):
        var_names = [
            ('temperature', 'Temperatur'),
            ('salinity', 'Salinity'),
            ('pressure', 'Depth')
        ]
        data = self.data[self._find_tag('VARIABLES', self.data):]
        var_cols = {var: data[0].index(header) for var, header in var_names}

        for line in data[3:]:
            for variable, header in var_names:
                column = var_cols[variable]
                value = line[column]
                try:
                    value = None if value == MISSING_VALUE else float(value)
                except ValueError:
                    logging.exception('Exception while converting {} to '
                                      'float'.format(value))
                    value = None

                self.variables[variable].append(value)

    def _parse_time(self, header):
        field_names = ['Year', 'Month', 'Day', 'Time']
        time_vals = self._header_vals(field_names, header)
        ymd = [int(x) for x in time_vals[:3]]
        date_time = datetime(*ymd)
        hours = timedelta(hours=float(time_vals[3] or 1))
        return datetime.strftime(date_time+hours, '%Y-%m-%dT%H:%M:%S')

    def _parse_lat_lon(self, header):
        lat_lon_vals = self._header_vals(['Latitude', 'Longitude'], header)
        return [float(x) for x in lat_lon_vals]

    def _header_vals(self, tags, header):
        vals = []
        tags = [tags] if type(tags) == str else tags
        for tag in tags:
            ind = self._find_tag(tag, header)
            if ind is not None:
                vals.append(header[ind][2])
            else:
                vals.append(None)
        return vals

    def _find_tag(self, tag, data):
        for i, line in enumerate(data):
            if line[0] == tag:
                return i
