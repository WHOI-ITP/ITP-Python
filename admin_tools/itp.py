REQUIRED_VARIABLES = ['pressure', 'temperature', 'salinity']
REQUIRED_METADATA = ['latitude', 'longitude', 'date_time', 'system_number',
                     'profile_number', 'source']


class ItpProfile:
    def __init__(self, metadata, variables):
        assert set(REQUIRED_VARIABLES).issubset(variables)
        assert set(REQUIRED_METADATA).issubset(metadata)
        self._metadata = metadata
        self._variables = variables

    def metadata(self, field):
        return self._metadata[field]

    def n_samples(self):
        return len(self._variables['pressure'])

    def variables(self):
        return list(self._variables.keys())

    def data(self, field):
        return self._variables[field]

    def scaled_data(self, field):
        """
        This is used to read data before writing to the database.
        """
        return [None if x is None else int(x * 10000)
                for x in self.data(field)]
