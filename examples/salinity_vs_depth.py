from itp.itp_query import ItpQuery
from datetime import datetime
import matplotlib.pyplot as plt


path = 'J:/ITP Data/itp_final_2021_11_09.db'
time_range = [datetime(2010, 1, 1), datetime(2010, 12, 31)]
query = ItpQuery(path, latitude=[70, 80], longitude=[-170, -140], date_time=time_range)
results = query.fetch()

fig, ax = plt.subplots()
ax.plot(results[0].salinity, results[0].pressure)
ax.invert_yaxis()
ax.set_xlabel('Salinity')
ax.set_ylabel('Pressure (dbar)')
plt.show()
