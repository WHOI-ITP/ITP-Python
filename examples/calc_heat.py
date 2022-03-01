from itp.itp_query import ItpQuery, Profile
from examples.heat import calc_heat
from pathlib import Path
import numpy as np
from datetime import datetime
import pickle


# def load_ctd(directory, pattern, time_range):
#     files = Path(directory).glob(pattern)
#     profiles = []
#     for file in files:
#         this_profile = Profile()
#         with file.open(mode='r') as fid:
#             this_profile.profile_number = int(fid.readline().strip())
#             this_profile.latitude = float(fid.readline().strip())
#             this_profile.longitude = float(fid.readline().strip())
#             time = datetime.strptime(fid.readline().strip(), '%d-%b-%Y %H:%M:%S')
#             if not (time_range[0] <= time <= time_range[1]):
#                 print(f'time out of range: {time}')
#                 continue
#             this_profile.date_time = time
#             this_profile.system_number = 999
#             this_profile.source = file.name
#             data = np.loadtxt(fid, delimiter=',')
#             if data.size <= 3:
#                 continue
#             this_profile.pressure = data[:, 0]
#             this_profile.salinity = data[:, 2]
#             this_profile.temperature = data[:, 1]
#             profiles.append(this_profile)
#     return profiles
#
#
path = r'D:\ITP Data\grid\itp_grid_2020_02_03.db'
#
# time_range = [datetime(2018, 1, 1), datetime(2020, 1, 1)]
# query = ItpQuery(path, latitude=[70, 81], longitude=[-169, -129], date_time=time_range)
# query.set_max_results(20000)
# itp_profiles = query.fetch()
# ctd_profiles = load_ctd('C:/Projects/heat_content/', '*.txt', time_range)
# itp_profiles.extend(ctd_profiles)
# itp_profiles = calc_heat(itp_profiles, [31, 33], method='salt')
#
#
# with open('heat_output.txt', 'w') as fid:
#     for profile in itp_profiles:
#         if not hasattr(profile, 'heat'):
#             continue
#         fid.write(f'{profile.latitude}, {profile.longitude}, {profile.heat}, {profile.thickness}\n')



meta_data = []
for system in range(150):
    print(f'Processing ITP{system}')
    query = ItpQuery(path, system=[system])
    query.set_max_results(20000)
    itp_profiles = query.fetch()
    itp_profiles = itp_profiles
    itp_profiles = calc_heat(itp_profiles, [10, 700])

    for profile in itp_profiles:
        if not hasattr(profile, 'heat'):
            continue
        this_meta_data = {
            'latitude': profile.latitude,
            'longitude': profile.longitude,
            'heat': profile.heat,
            'date_time': profile.date_time,
            'system': profile.system_number
        }
        meta_data.append(this_meta_data)


for profile in meta_data:
    profile['posix_time'] = datetime.strptime(profile['date_time'], '%Y-%m-%dT%H:%M:%S').timestamp()


with open('meta_data.txt', 'wb') as fid:
    pickle.dump(meta_data, fid)
