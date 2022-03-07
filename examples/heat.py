import numpy as np
import gsw


DEPTH_THRESHOLD = 10
SALT_THRESHOLD = 0.1


def calc_heat(profiles, bounds, method='depth'):
    """
    take a list of Profile objects and add heat, thickness, and average temperature
    """
    assert len(bounds) == 2, 'bounds must be a two element list'
    assert bounds[0] < bounds[1], 'bounds[0] must be less than bounds[1]'
    assert method in ['depth', 'salt'], f'Unknown bounding method "{method}".'

    for profile in profiles:
        remove_none_vals(profile)
        if method == 'depth':
            array = profile.depth()
            threshold = DEPTH_THRESHOLD
        else:
            array = profile.salinity
            threshold = SALT_THRESHOLD
        ind = get_indices(array, bounds, threshold)
        if ind is None:
            continue
        heat_capacity = gsw.cp_t_exact(
            profile.absolute_salinity(),
            profile.temperature,
            profile.pressure
        )
        freeze = gsw.t_freezing(profile.absolute_salinity(), profile.pressure, 1)
        heat = profile.density() * heat_capacity * (profile.temperature - freeze)
        profile.heat = np.trapz(heat[ind], profile.depth()[ind])
        profile.thickness = profile.depth()[ind[-1]] - profile.depth()[ind[0]]
        profile.avg_temp = np.trapz(profile.temperature[ind], profile.depth()[ind]) / profile.thickness
    return profiles


def remove_none_vals(profile):
    not_none = np.where((profile.temperature is not None) & (profile.salinity is not None))[0]
    profile.salinity = profile.salinity[not_none]
    profile.temperature = profile.temperature[not_none]
    profile.pressure = profile.pressure[not_none]


def get_indices(array, bounds, threshold):
    ind = np.where((array >= bounds[0]) & (array <= bounds[1]))[0]
    if len(ind) < 2:
        return None
    if abs(array[ind[0]] - bounds[0]) > threshold:
        return None
    if abs(array[ind[-1]] - bounds[1]) > threshold:
        return None
    return ind
