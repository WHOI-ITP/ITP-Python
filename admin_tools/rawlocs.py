from admin_tools.ctd_parser import CTDParser
from admin_tools.utils import julian_to_iso8601
from pathlib import Path
import re


YEAR = 0
DAY = 1
LONGITUDE = 2
LATITUDE = 3


class RawlocsCollection:
    def __init__(self, paths):
        if type(paths) == str:
            paths = [paths]
        self.paths = paths

    @classmethod
    def glob(cls, parent_directory):
        paths = list(Path(parent_directory).glob('**/itp*rawlocs.dat'))
        return cls(paths)

    def __iter__(self):
        for path in self.paths:
            with open(path, 'r') as f:
                rawlocs = RawlocsFile(f.readlines(), Path(path).name)
                rawlocs.parse()
                yield rawlocs


class RawlocsFile:
    def __init__(self, data, source):
        self.data = [line.strip() for line in data]
        self.source = source
        self.system_number = None
        self.date_time = []
        self.latitude = []
        self.longitude = []

    def parse(self):
        system_re = re.search(r'itp([0-9]+)rawlocs.dat', self.source)
        self.system_number = int(system_re.group(1))
        for row in self.data:
            values = row.split()
            if row[0].startswith('%endofdat'):
                break
            if row[0].startswith('%'):
                continue  # skip comments, including header
            # values = [None if v == 'NaN' else float(v) for v in values]
            year_day = (int(values[YEAR]), float(values[DAY]))
            self.date_time.append(julian_to_iso8601(*year_day))
            self.latitude.append(float(values[LATITUDE]))
            lon = float(values[LONGITUDE])
            self.longitude.append((lon + 180) % 360 - 180)
