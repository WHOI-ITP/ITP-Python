"""
Parse a direction file and return a dict of directions. The key is a
tuple of (system, profile).

Only 'up' and 'down' are returned. Not all profiles have direction.
"""


def get_direction(path):
    profiles = {}
    with open(path, 'r') as f:
        f.readline()
        line = f.readline().strip()
        while line:
            data = [x.strip() for x in line.split('\t')]
            system, profile, direction = data
            if direction in ['up', 'down']:
                profiles[(int(system), int(profile))] = direction
            line = f.readline().strip()
    return profiles
