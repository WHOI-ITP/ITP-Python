from datetime import datetime
import gsw


class Profile:
    def __init__(self):
        self._id = None
        self.system_number = None
        self.profile_number = None
        self.date_time = None
        self.latitude = None
        self.longitude = None
        self.pressure = None
        self.salinity = None
        self.temperature = None
        self.source = None

    def python_datetime(self):
        return datetime.strptime(self.date_time, '%Y-%m-%dT%H:%M:%S')

    def posix_time(self):
        return self.python_datetime().timestamp()

    def depth(self):
        return -self.height()

    def height(self):
        return gsw.conversions.z_from_p(self.pressure, self.latitude)

    def absolute_salinity(self):
        return gsw.conversions.SA_from_SP(
            self.salinity,
            self.pressure,
            self.longitude,
            self.latitude
        )

    def conservative_temperature(self):
        return gsw.conversions.CT_from_t(
            self.absolute_salinity(),
            self.temperature,
            self.pressure
        )

    def density(self):
        return gsw.density.rho(
            self.absolute_salinity(),
            self.conservative_temperature(),
            self.pressure
        )

    def potential_temperature(self, p_ref=0):
        return gsw.conversions.pt_from_t(
            self.absolute_salinity(),
            self.temperature,
            self.pressure,
            p_ref
        )

    def freezing_temperature_zero_pressure(self):
        return gsw.CT_freezing(
            self.absolute_salinity(),
            p=0,
            saturation_fraction=1
        )

    def heat_capacity(self):
        return gsw.cp_t_exact(
            self.absolute_salinity(),
            self.temperature,
            self.pressure
        )
