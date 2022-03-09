from mpl_toolkits.basemap import Basemap
from itp.itp_query import ItpQuery
import matplotlib.pyplot as plt


path = 'J:/ITP Data/itp_final_2021_11_09.db'
query = ItpQuery(path, system=[1])
results = query.fetch()

longitude = [p.longitude for p in results]
latitude = [p.latitude for p in results]
m = Basemap(projection='npstere', boundinglat=70, lon_0=0, resolution='i')
m.drawcoastlines()
m.fillcontinents()
m.drawparallels(range(70, 90, 5))
m.drawmeridians(range(-180, 180, 20), latmax=85)
m.plot(longitude, latitude, latlon=True)
plt.show()
