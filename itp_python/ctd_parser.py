from itp_python.itp import ItpProfile


class CTDParser:
    def __init__(self, data, source):
        self.data = [line.strip() for line in data]
        self.metadata = dict()
        self.metadata['source'] = source
        self.variables = {'temperature': list(),
                          'pressure': list(),
                          'salinity': list()}

    def parse(self):
        self.parse_header()
        self.read_data()
        return ItpProfile(self.metadata, self.variables)

    def parse_header(self):
        raise NotImplementedError

    def read_data(self):
        raise NotImplementedError
