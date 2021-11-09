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
            system, profile, direction = line.split('\t')
            if direction in ['up', 'down']:
                profiles[(system, profile)] = direction
            line = f.readline().strip()
    return profiles
