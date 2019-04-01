from itp_python.utils import julian_to_iso8601
from itp_python.itp import Itp, itp_metadata
from pathlib import Path
import re


def parse_itp_final(path):
    with open(path) as datafile:
        header = [datafile.readline(),
                  datafile.readline(),
                  datafile.readline()]
        metadata, sensor_names = _parse_header(header)
        sensors = _init_data_dict(sensor_names)
        for row in datafile:
            if row.startswith('%'):
                continue
            values = row.split()
            for i, field in enumerate(sensor_names):
                sensors[field].append(values[i])
    metadata['file_name'] = Path(path).name
    return Itp(metadata, sensors)


def _parse_header(header):
    metadata = itp_metadata()
    header_re = re.search('%ITP ([0-9]+).*profile ([0-9]+)', header[0])
    metadata['system_number'] = int(header_re.group(1))
    metadata['profile_number'] = int(header_re.group(2))
    date_and_pos = header[1].split()
    year_day = (int(date_and_pos[0]), float(date_and_pos[1]))
    metadata['date_time'] = julian_to_iso8601(*year_day)
    metadata['longitude'] = float(date_and_pos[2])
    metadata['latitude'] = float(date_and_pos[3])
    metadata['n_depths'] = int(date_and_pos[4])
    sensor_names = re.sub('%|\([^)]*\)', '', header[2])
    return metadata, sensor_names.split()

def _init_data_dict(sensor_names):
    sensors = dict.fromkeys(sensor_names)
    for sensor in sensors.keys():
        sensors[sensor] = list()
    return sensors