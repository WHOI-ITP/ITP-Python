from admin_tools.utils import julian_to_iso8601
from pathlib import Path
from admin_tools.ctd_parser import CTDParser
from admin_tools.profile_direction import get_direction
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
    def __init__(self, paths, direction=None):
        if type(paths) == str:
            paths = [paths]
        self.paths = paths
        self.direction = direction if direction else {}

    @classmethod
    def glob(cls, parent_directory):
        paths = list(Path(parent_directory).glob('**/itp*grd*.dat'))
        direction_file = Path(parent_directory) / 'direction.txt'
        if direction_file.is_file():
            direction = get_direction(direction_file)
        else:
            direction = None
        return cls(paths, direction)

    def __iter__(self):
        for path in self.paths:
            with open(path, 'r') as f:
                parser = ITPFinalParser(f.readlines(), Path(path).name)
                parser.add_direction(self.direction)
                yield parser.parse()


class ITPFinalParser(CTDParser):
    def __init__(self, data, source):
        super().__init__(data, source)
        self.direction = {}

    def parse_header(self):
        header_search = re.search(r'%ITP ([0-9]+).*profile ([0-9]+)',
                                  self.data[SYSTEM_CAST_LINE])
        self.metadata['system_number'] = int(header_search.group(SYSTEM))
        self.metadata['profile_number'] = int(header_search.group(PROFILE))
        date_and_pos = self.data[DATE_POS_LINE].split()
        year_day = (int(date_and_pos[YEAR]), float(date_and_pos[DAY]))
        self.metadata['date_time'] = julian_to_iso8601(*year_day)
        lon = float(date_and_pos[LONGITUDE])
        self.metadata['longitude'] = (lon + 180) % 360 - 180
        self.metadata['latitude'] = float(date_and_pos[LATITUDE])
        key = (self.metadata['system_number'], self.metadata['profile_number'])
        if key in self.direction:
            self.metadata['direction'] = self.direction[key]

    def add_direction(self, direction):
        self.direction = direction

    def read_data(self):
        for row in self.data[DATA_START:]:
            values = row.split()
            if row[0].startswith('%'):
                continue  # skip comments, including header
            values = [None if v == 'NaN' else float(v) for v in values]
            for i, field in enumerate(self.variables):
                if field in self.variables.keys():
                    self.variables[field].append(values[i])

    def get_variable_names(self):
        # Ger variable names and create a dict with the names as keys
        # remove percent sign, parentheses (with contents), and x10^4
        variable_names = re.sub(r'%|x10\^4|\([^)]*\)', '',
                                self.data[VARIABLES_LINE])
        variable_names = re.sub(r'-', '_', variable_names)
        variable_names = variable_names.lower().split()
        if 'nobs' in variable_names:
            variable_names.remove('nobs')
        self.variables = {v: list() for v in variable_names}
