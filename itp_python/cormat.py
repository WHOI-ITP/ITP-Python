import numpy as np
import h5py
import re
import operator
from collections.abc import Iterable
from pathlib import Path
from datetime import datetime
from itp_python.itp import ItpProfile


def to_string(array):
    return ''.join(chr(x) for x in array)


class CormatCollection(Iterable):
    def __init__(self, directory, pattern='**/cor*.mat', filt=None):
        self.files = Path(directory).glob(pattern)
        self.filt = filt

    def __iter__(self):
        for file_path in self.files:
            file = CormatParser(file_path, self.filt).parse()
            if file:
                yield file


class CormatParser:
    REQUIRED = {'latitude', 'longitude', 'itpno', 'psdate', 'pstart',
                'pr_filt', 'te_cor', 'sa_adj'}

    def __init__(self, path, filt):
        self.path = Path(path)
        self.filt = filt
        self.metadata = {}
        self.variables = {}
        self.filename_re = re.compile(r'cor([0-9]+).mat')

    def parse(self):
        try:
            with h5py.File(self.path, 'r') as file:
                if not self.check_required_dsets(file):
                    return
                self.parse_metadata(file)
                if not in_filter(self.metadata, self.filt):
                    return
                self.parse_data(file)
                return ItpProfile(self.metadata, self.variables)
        except OSError:
            pass

    def check_required_dsets(self, file):
        if self.REQUIRED.issubset(file.keys()):
            return True

    def parse_metadata(self, file):
        m = self.metadata
        m['source'] = self.path.name
        m['latitude'] = np.array(file.get('latitude'))[0][0]
        lon = np.array(file.get('longitude'))[0][0]
        m['longitude'] = (lon + 180) % 360 - 180
        m['system_number'] = int(np.array(file.get('itpno'))[0][0])
        m['profile_number'] = int(re.search(self.filename_re,
                                            self.path.name).group(1))
        time_str = '{} {}'.format(
            to_string(np.array(file.get('psdate'))),
            to_string(np.array(file.get('pstart'))))
        date_time = datetime.strptime(time_str, '%m/%d/%y %H:%M:%S')
        m['date_time'] = datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%S')

    def parse_data(self, file):
        v = self.variables
        data = np.stack([
            np.array(file.get('pr_filt'))[0],
            np.array(file.get('te_cor'))[0],
            np.array(file.get('sa_adj'))[0]])
        is_nan_col = np.isnan(data).any(axis=0)
        data = data[:, ~is_nan_col]
        if self.metadata['profile_number'] % 2 == 1:
            data = np.fliplr(data)

        v['pressure'] = self.make_list(data[0, :])
        v['temperature'] = self.make_list(data[1, :])
        v['salinity'] = self.make_list(data[2, :])

    def make_list(self, data):
        return [x for x in data]


def in_filter(metadata, filt=None):
    status = True
    filt = filt or {}
    lat_range = filt.get('latitude', None)
    lon_range = filt.get('longitude', None)
    if lat_range:
        is_lat = lat_range[0] <= metadata['latitude'] < lat_range[1]
        status = status and is_lat
    if lon_range:
        op = operator.or_ if lon_range[1] < lon_range[0] else operator.and_
        is_lon = op(metadata['longitude'] > lon_range[0],
                    metadata['longitude'] < lon_range[1])
        status = status and is_lon
    return status
