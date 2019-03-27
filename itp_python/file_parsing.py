from itp_python.utils import julian_to_iso8601
import re


class ItpFinal:
    def __init__(self, path):
        self.path = path
        self.system_number = None
        self.profile_number = None
        self.date_time = None
        self.latitude = None
        self.longitude = None
        self.channels = {}
        self.n_depths = 0

    def parse_data(self):
        with open(self.path) as datafile:
            header = [datafile.readline(),
                      datafile.readline(),
                      datafile.readline()]
            self._parse_header(header)

            for row in datafile:
                values = row.split()
                if len(values) != len(self.channels):
                    continue
                for i, field in enumerate(self.channels.keys()):
                    self.channels[field].append(values[i])

    def _parse_header(self, header):
        header_re = re.search('%ITP ([0-9]+), profile ([0-9]+)', header[0])
        self.system_number = int(header_re.group(1))
        self.profile_number = int(header_re.group(2))

        date_and_pos = header[1].split()
        self.date_time = julian_to_iso8601(int(date_and_pos[0]),
                                           float(date_and_pos[1]))
        self.longitude = float(date_and_pos[2])
        self.latitude = float(date_and_pos[3])
        self.n_depths = int(date_and_pos[4])

        column_header = re.sub('%|\([^)]*\)', '', header[2])
        self.channels = dict.fromkeys(column_header.split())
        for field in self.channels.keys():
            self.channels[field] = list()

