import matplotlib.pyplot as plt
import numpy as np
from itp.itp_query import ItpQuery
from geopy.distance import distance


PATH = r'D:\ITP Data\itp_final_2020_09_14.db'
DEPTH_GRID = np.arange(0, 301)

# Create an ItpQuery object
query = ItpQuery(PATH, system=[1], pressure=[0, DEPTH_GRID.max()])
results = query.fetch()

# extract lat and lon from results
longitude = np.array([p.longitude for p in results])
latitude = np.array([p.latitude for p in results])

# calculate distance between stations
dist = []
for i in range(len(latitude)-1):
    p1 = (latitude[i], longitude[i])
    p2 = (latitude[i+1], longitude[i+1])
    dist.append(distance(p1, p2).km)

# cumulative drift distance
cumulative_dist = np.hstack([0, np.cumsum(dist)])

# make grids from distance and depth (to be used with contourf)
dist_grid, depth_grid = np.meshgrid(cumulative_dist, DEPTH_GRID)
temp_grid = np.zeros(np.shape(dist_grid))

# interpolate profiles to a 0 to 300 meter depth grid
for i in range(len(results)):
    temp_grid[:, i] = np.interp(
        DEPTH_GRID,
        results[i].depth(),
        results[i].potential_temperature())

fig, ax = plt.subplots()
contour = ax.contourf(dist_grid, depth_grid, temp_grid)
ax.invert_yaxis()
colorbar = fig.colorbar(contour)
colorbar.ax.set_ylabel('Potential Temperature (C)')
ax.set_xlabel('Drift Distance (km)')
ax.set_ylabel('Depth (m)')