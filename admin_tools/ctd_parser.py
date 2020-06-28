from admin_tools.itp import ItpProfile


class CTDParser:
    def __init__(self, data, source):
        self.data = [line.strip() for line in data]
        self.metadata = dict()
        self.metadata['source'] = source
        self.variables = dict()

    def parse(self):
        self.parse_header()
        self.get_variable_names()
        self.read_data()
        return ItpProfile(self.metadata, self.variables)

    def parse_header(self):
        raise NotImplementedError

    def get_variable_names(self):
        raise NotImplementedError

    def read_data(self):
        raise NotImplementedError
