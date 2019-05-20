from itp_python.utils import julian_to_iso8601
from itp_python.itp import Itp, SENSOR_PRECISION
from pathlib import Path
import re


def parse_itp_final(path):
    with open(path) as datafile:
        header = [datafile.readline(),
                  datafile.readline(),
                  datafile.readline()]
        metadata, sensor_names = _parse_header(header)
        metadata['file_name'] = Path(path).name
        sensors = _init_data_dict(sensor_names)
        for row in datafile:
            if row.startswith('%'):
                continue
            values = row.split()
            values = [None if v == 'NaN' else float(v) for v in values]
            for i, field in enumerate(sensor_names):
                scale = SENSOR_PRECISION.get(field, 0)
                data = None if values[i] is None else int(values[i] * 10 ** scale)
                sensors[field].append(data)
    return metadata, sensors


def _parse_header(header):
    header_re = re.search('%ITP ([0-9]+).*profile ([0-9]+)', header[0])
    metadata = {}
    metadata['system_number'] = int(header_re.group(1))
    metadata['profile_number'] = int(header_re.group(2))
    date_and_pos = header[1].split()
    year_day = (int(date_and_pos[0]), float(date_and_pos[1]))
    metadata['date_time'] = julian_to_iso8601(*year_day)
    metadata['longitude'] = float(date_and_pos[2])
    metadata['latitude'] = float(date_and_pos[3])
    metadata['n_depths'] = int(date_and_pos[4])
    # remove left paren "(" and everything after
    sensor_names = re.sub('%|(\(\S*)*', '', header[2])
    return metadata, sensor_names.split()


def _init_data_dict(sensor_names):
    sensors = dict.fromkeys(sensor_names)
    for sensor in sensors.keys():
        sensors[sensor] = list()
    return sensors
