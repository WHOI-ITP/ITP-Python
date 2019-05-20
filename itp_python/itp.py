
REQUIRED_SENSORS = ['pressure', 'temperature', 'salinity', 'nobs']
SENSOR_PRECISION = {'pressure': 1,
                    'temperature': 4,
                    'salinity': 4}


class Itp:
    def __init__(self, metadata, sensors):
        assert set(REQUIRED_SENSORS).issubset(sensors)
        self.metadata = metadata
        self.sensors = sensors

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
        scale = SENSOR_PRECISION.get(sensor, 0)
        return [None if x is None else x/(10**scale)
                for x in self.sensors[sensor]]
