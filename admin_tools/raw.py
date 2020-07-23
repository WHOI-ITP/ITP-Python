import numpy as np
import h5py
import re
from collections.abc import Iterable
from pathlib import Path
from datetime import datetime
from admin_tools.itp import ItpProfile
import gsw


def to_string(array):
    return ''.join(chr(x) for x in array)


def load_position(directory):
    location_file = list(Path(directory).glob('itp*loci.mat'))
    assert len(location_file) == 1
    location_file = location_file[0]
    position = {}
    with h5py.File(location_file, 'r') as file:
        position['latitude'] = np.array(file.get('lat')[0])
        position['longitude'] = np.array(file.get('lon')[0])
        return position


class RawCollection(Iterable):
    def __init__(self, directories):
        self.directories = directories

    @classmethod
    def glob(cls, directory):
        # a little different than the other subclasses
        # this is a hack. Raw files have a separate .mat file that contains
        # positions... very annoying

        paths = [p for p in Path(directory).glob('itp*rawmat') if p.is_dir()]
        return cls(paths)

    def __iter__(self):
        # NOTE self.paths contain directories, not individual files as with
        # cormat, final, etc.
        for directory in self.directories:
            print(directory)
            position = load_position(directory)
            for i, path in enumerate(directory.glob('raw*.mat')):
                file = RawParser(path, position, i).parse()
                if file:
                    yield file


class RawParser:
    REQUIRED = {'cpres', 'ctemp', 'ccond', 'pstart', 'psdate'}

    def __init__(self, path, position, index):
        self.path = path
        self.position = position
        self.index = index
        self.metadata = {}
        self.variables = {}
        self.filename_re = re.compile(r'raw([0-9]+).mat')
        self.system_re = re.compile(r'itp([0-9]+)rawmat')

    def parse(self):
        try:
            with h5py.File(self.path, 'r') as file:
                if not self.check_required_dsets(file):
                    return
                self.parse_metadata(file)
                self.parse_data(file)
                if len(self.variables['pressure']) != 0:
                    return ItpProfile(self.metadata, self.variables)
        except OSError as e:
            print(e)
        except IndexError as e:
            print(e)

    def check_required_dsets(self, file):
        if self.REQUIRED.issubset(file.keys()):
            return True

    def parse_metadata(self, file):
        m = self.metadata
        m['source'] = self.path.name
        m['latitude'] = self.position['latitude'][self.index]
        lon = self.position['longitude'][self.index]
        m['longitude'] = (lon + 180) % 360 - 180
        m['system_number'] = int(re.search(self.system_re,
                                           str(self.path)).group(1))
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
            np.array(file.get('cpres'))[0],
            np.array(file.get('ctemp'))[0],
            np.array(file.get('ccond'))[0]])
        is_nan_col = np.isnan(data).any(axis=0)
        data = data[:, ~is_nan_col]
        if self.metadata['profile_number'] % 2 == 1:
            data = np.fliplr(data)

        self.variables['pressure'] = self.make_list(data[0, :])
        self.variables['temperature'] = self.make_list(data[1, :])
        salinity = gsw.SP_from_C(data[2, :], data[1, :], data[0, :])
        self.variables['salinity'] = self.make_list(salinity)

    def make_list(self, data):
        return [x for x in data]

