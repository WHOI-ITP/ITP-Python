import numpy as np
import matplotlib.pyplot as plt
from itp.itp_query import ItpQuery
from datetime import datetime
from mpl_toolkits.basemap import Basemap


PATH = 'J:/ITP Data/itp_final_2021_11_09.db'
TIME_RANGE = [datetime(2006, 1, 1), datetime(2007, 12, 31)]

query = ItpQuery(
    PATH, latitude=[70, 80],
    longitude=[-180, -130],
    date_time=TIME_RANGE,
    pressure=[400, 402])
query.set_max_results(10000)  # override the 5000 result limit
results = query.fetch()

temp_400 = []
for profile in results:
    temp_400.append(profile.temperature[0])

longitude = np.array([p.longitude for p in results])
latitude = np.array([p.latitude for p in results])

m = Basemap(projection='npstere', boundinglat=70, lon_0=0, resolution='i')
m.drawcoastlines()
m.fillcontinents()
m.drawparallels(range(70, 90, 5))
m.drawmeridians(range(-180, 180, 20), latmax=85)
scatter = m.scatter(
    longitude, latitude, c=temp_400, latlon=True, vmin=0.3, vmax=1.0)
colorbar = plt.colorbar(scatter)
colorbar.ax.set_ylabel('Temperature (C)')
plt.show()
