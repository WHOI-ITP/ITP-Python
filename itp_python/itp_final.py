from itp_python.utils import julian_to_iso8601
from pathlib import Path
from itp_python.ctd_parser import CTDParser
import re


SYSTEM_CAST_LINE = 0
DATE_POS_LINE = 1
VARIABLES_LINE = 2
DATA_START = 3
SYSTEM = 1
PROFILE = 2
YEAR = 0
DAY = 1
LONGITUDE = 2
LATITUDE = 3


class ITPFinalCollection:
    def __init__(self, paths):
        if type(paths) == str:
            paths = [paths]
        self.paths = paths

    @classmethod
    def glob(cls, parent_directory):
        paths = list(Path(parent_directory).glob('**/itp*grd*.dat'))
        return cls(paths)

    def __iter__(self):
        for path in self.paths:
            with open(path, 'r') as f:
                yield ITPFinalParser(f.readlines(), Path(path).name).parse()


class ITPFinalParser(CTDParser):
    def parse_header(self):
        header_search = re.search(r'%ITP ([0-9]+).*profile ([0-9]+)',
                                  self.data[SYSTEM_CAST_LINE])
        self.metadata['system_number'] = int(header_search.group(SYSTEM))
        self.metadata['profile_number'] = int(header_search.group(PROFILE))
        date_and_pos = self.data[DATE_POS_LINE].split()
        year_day = (int(date_and_pos[YEAR]), float(date_and_pos[DAY]))
        self.metadata['date_time'] = julian_to_iso8601(*year_day)
        self.metadata['longitude'] = float(date_and_pos[LONGITUDE])
        self.metadata['latitude'] = float(date_and_pos[LATITUDE])

    def read_data(self):
        variable_names = self._get_variable_names()
        for row in self.data[DATA_START:]:
            values = row.split()
            if row[0].startswith('%'):
                continue  # skip comments, including header
            values = [None if v == 'NaN' else float(v) for v in values]
            for i, field in enumerate(variable_names):
                if field in self.variables.keys():
                    self.variables[field].append(values[i])

    def _get_variable_names(self):
        # remove percent sign, parentheses (with contents), and x10^4
        sensor_names = re.sub(r'%|x10\^4|\([^)]*\)', '',
                              self.data[VARIABLES_LINE])
        sensor_names = re.sub(r'-', '_', sensor_names)
        sensor_names = sensor_names.lower()
        return sensor_names.split()

    def _init_data_dict(self, sensor_names):
        variables = dict.fromkeys(sensor_names)
        for sensor in variables.keys():
            variables[sensor] = list()
        return variables
