from itp_python.utils import julian_to_iso8601
from itp_python.itp import ItpProfile
from pathlib import Path
import re


class ITPFinalCollection:
    def __init__(self, parent_directory):
        self.parent_dir = parent_directory
        self.paths = list(Path(self.parent_dir).glob('**/itp*grd*.dat'))

    def __iter__(self):
        for path in self.paths:
            yield parse_itp_final(path)


def parse_itp_final(path):
    with open(path) as datafile:
        header = [datafile.readline(),
                  datafile.readline()]
        metadata = _parse_header(header)
        variables = _get_variables(datafile.readline())
        metadata['variables'] = variables
        metadata['source'] = Path(path).name
        variables = _init_data_dict(variables)
        for row in datafile:
            if row.startswith('%'):
                continue
            values = row.split()
            values = [None if v == 'NaN' else float(v) for v in values]
            for i, field in enumerate(variables):
                variables[field].append(values[i])
    return ItpProfile(metadata, variables)


def _parse_header(header):
    header_re = re.search(r'%ITP ([0-9]+).*profile ([0-9]+)', header[0])
    metadata = dict()
    metadata['system_number'] = int(header_re.group(1))
    metadata['profile_number'] = int(header_re.group(2))
    date_and_pos = header[1].split()
    year_day = (int(date_and_pos[0]), float(date_and_pos[1]))
    metadata['date_time'] = julian_to_iso8601(*year_day)
    metadata['longitude'] = float(date_and_pos[2])
    metadata['latitude'] = float(date_and_pos[3])
    # remove left paren "(" and everything after
    return metadata


def _get_variables(header):
    # remove percent sign, parenthesis (with contents), and x10^4
    sensor_names = re.sub(r'%|x10\^4|\([^)]*\)', '', header)
    sensor_names = re.sub(r'-', '_', sensor_names)
    sensor_names = sensor_names.lower()
    return sensor_names.split()


def _init_data_dict(sensor_names):
    variables = dict.fromkeys(sensor_names)
    for sensor in variables.keys():
        variables[sensor] = list()
    return variables
