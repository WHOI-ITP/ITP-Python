from datetime import datetime, timedelta
from admin_tools.itp import ItpProfile
from pathlib import Path
from admin_tools.ctd_parser import CTDParser
import logging
from collections.abc import Iterable


logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y/%m/%dT%I:%M:%S',
                    filename='../itp_python/wod_csv.log',
                    filemode='w',
                    level=logging.DEBUG)

MISSING_VALUE = '---0---'


class WODCollection(Iterable):
    def __init__(self, paths):
        self.paths = paths

    @classmethod
    def glob(cls, parent_directory):
        paths = list(Path(parent_directory).glob('**/*.CTD*.csv'))
        return cls(paths)

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
                        yield WODParser(data, 'WOD data').parse()
                    except ValueError:
                        return None
                    except TypeError:
                        logging.exception('Exception caught during parsing')


class WODParser(CTDParser):
    NAME_COL = 0
    DATA_COL = 2
    # (name in Wod File, name in itp db, data type)
    METADATA_FIELDS = [
        ('CAST',  'profile_number', int),
        ('Latitude', 'latitude', float),
        ('Longitude', 'longitude', float),
        ('NODC Cruise ID', 'system_number', str)
    ]
    TIME_FIELDS = ['Year', 'Month', 'Day', 'Time']

    def __init__(self, data, source):
        super().__init__(data, source)
        self.data = [[value.strip() for value in line.split(',')]
                     for line in data]

    def parse_header(self):
        header = self._header()
        for wod_name, metadata_name, _type in self.METADATA_FIELDS:
            self.metadata[metadata_name] = _type(header[wod_name])
        self.metadata['date_time'] = self._parse_time(header)

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

    def _header(self):
        header_vals = {}
        header = self.data[:self._find_tag('METADATA', self.data)]
        for line in header:
            header_vals[line[self.NAME_COL]] = line[self.DATA_COL]
        return header_vals

    def _parse_time(self, header):
        field_names = ['Year', 'Month', 'Day']
        time_vals = [int(header[field]) for field in field_names]
        date_time = datetime(*time_vals)
        # not all profiles have a Time field
        hours = timedelta(hours=float(header.get('Time', 0)))
        return datetime.strftime(date_time+hours, '%Y-%m-%dT%H:%M:%S')

    def _find_tag(self, tag, data):
        for i, line in enumerate(data):
            if line[self.NAME_COL] == tag:
                return i
