import numpy as np
import re
from admin_tools.itp import ItpProfile
from admin_tools.rawlocs import RawlocsFile
from admin_tools.utils import julian_to_iso8601
from datetime import datetime
from pathlib import Path


VARIABLES_LINE = 1
DATA_START = 2

SYSTEM = 1
PRESSURE = 2

YEAR = 0
DAY = 1


class ITPMicroCollection:
    def __init__(self, paths):
        if type(paths) == str:
            paths = [paths]
        self.paths = paths

    @classmethod
    def glob(cls, parent_directory):
        paths = list(Path(parent_directory).glob('**/itp*micro*.dat'))
        return cls(paths)

    def __iter__(self):
        for path in self.paths:
            # expects a itpXXXrawlocs.dat file in same directory
            number = re.search('itp([0-9]+)', path.name)[1]
            raw_locs_path = path.parent / ('itp' + number + 'rawlocs.dat')
            raw_locs = self.parse_raw_locs(raw_locs_path)
            with open(path, 'r') as f:
                parser = MicrocatParser(f.readlines(),
                                        raw_locs,
                                        Path(path).name)
                for station in parser.next_station():
                    yield station

    def parse_raw_locs(self, path):
        with open(path) as fid:
            raw_locs = RawlocsInterp(fid.readlines(), path.name)
        raw_locs.parse()
        return raw_locs


class MicrocatParser:
    def __init__(self, data, rawlocs, source):
        self.data = data
        self.rawlocs = rawlocs
        self.metadata = dict()
        self.metadata['source'] = source
        self.variables = dict()
        filename_re = re.search('itp([0-9]+)micro([0-9]*).dat', source)
        micro_n = int(filename_re[2])-1 if filename_re[2] else 0
        self.station_offset = micro_n * 1000000
        self.metadata['system_number'] = int(filename_re[1])
        self.parse_header()
        self.get_variable_names()

    def parse_header(self):
        search = '(?:microcat|micro-odo) ([0-9]+)(?:.*?([0-9\.]+) dbar)?'
        header_search = re.search(search, self.data[0])
        self.pressure = header_search[PRESSURE]
        if self.pressure:
            self.pressure = float(self.pressure)

    def get_variable_names(self):
        ignore = {'year', 'day'}
        # remove percent sign, parentheses (with contents), and x10^4
        variable_names = re.sub(r'%|x10\^4|\([^)]*\)', '',
                                self.data[VARIABLES_LINE])
        variable_names = re.sub(r'-', '_', variable_names)
        variable_names = variable_names.lower().split()
        self.columns = list(variable_names)
        to_remove = set(variable_names).intersection(ignore)
        for var in to_remove:
            variable_names.remove(var)
        self.variables = {v: list() for v in variable_names}
        self.variables['pressure'] = list()  # in case there's no pres column

    def next_station(self):
        for i, row in enumerate(self.data[DATA_START:]):
            values = row.split()
            if row[0].startswith('%'):
                continue  # skip comments, including header
            values = [None if v == 'NaN' else float(v) for v in values]
            year_day = (int(values[YEAR]), float(values[DAY]))
            iso8601_time = julian_to_iso8601(*year_day)
            self.metadata['date_time'] = iso8601_time
            timestamp = datetime.fromisoformat(iso8601_time).timestamp()
            lat, lon = self.rawlocs.interp_lat_lon(timestamp)
            self.metadata['latitude'] = lat
            self.metadata['longitude'] = lon
            self.metadata['profile_number'] = i + self.station_offset

            for v in self.variables:
                self.variables[v] = list()

            for i, field in enumerate(self.columns):
                if field in self.variables.keys():
                    self.variables[field].append(values[i])
            if not self.variables['pressure']:
                self.variables['pressure'] = [self.pressure]
            yield ItpProfile(self.metadata, self.variables)


class RawlocsInterp(RawlocsFile):
    def parse(self):
        super().parse()
        self._prepare_for_interp()

    def _prepare_for_interp(self):
        self.unit_vector = []
        self.timestamp = []
        for i in range(len(self.latitude)):
            lat, lon = self.latitude[i], self.longitude[i]
            self.unit_vector.append(self.lat_lon_to_xyz(lat, lon))
            self.timestamp.append(
                datetime.fromisoformat(self.date_time[i]).timestamp())
        self.unit_vector = np.array(self.unit_vector)
        self.timestamp = np.array(self.timestamp)

    def interp_lat_lon(self, timestamp):
        """ return lat/lon position based on timestamp """
        lat = np.interp(timestamp, self.timestamp, self.latitude)
        x = np.interp(timestamp, self.timestamp, self.unit_vector[:, 0])
        y = np.interp(timestamp, self.timestamp, self.unit_vector[:, 1])
        _, lon = self.xyz_to_lat_lon(x, y, 0)
        return lat, lon

    @staticmethod
    def lat_lon_to_xyz(lat, lon):
        lat, lon = np.deg2rad(lat), np.deg2rad(lon)
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        return x, y, z

    @staticmethod
    def xyz_to_lat_lon(x, y, z):
        lat = np.rad2deg(np.arcsin(z))
        lon = np.rad2deg(np.arctan2(y, x))
        return lat, lon
