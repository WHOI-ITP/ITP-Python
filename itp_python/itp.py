def itp_metadata():
    return {
        'system_number': None,
        'profile_number': None,
        'file_name': None,
        'date_time': None,
        'latitude': None,
        'longitude': None,
        'n_depths': None
    }


class Itp:
    def __init__(self, metadata, sensors):
        self.metadata = metadata
        self.sensors = sensors
        assert {'pressure', 'temperature', 'salinity'}.issubset(self.sensors)

    @property
    def latitude(self):
        return self.metadata['latitude']

    @property
    def longitude(self):
        return self.metadata['longitude']

    @property
    def date_time(self):
        return self.metadata['date_time']

    @property
    def system_number(self):
        return self.metadata['system_number']

    @property
    def profile_number(self):
        return self.metadata['profile_number']

    @property
    def file_name(self):
        return self.metadata['file_name']

    @property
    def n_depths(self):
        return self.metadata['n_depths']

    def active_sensors(self):
        return self.sensors.keys()

    def data(self, sensor):
        return self.sensors[sensor]


class ItpCollection:
    def __init__(self):
        pass
