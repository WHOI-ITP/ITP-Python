# ITP-Python
The Ice Tethered Profiler is an autonomous instrument that vertically profiles the water column under sea ice. The ITP collects measurements of conductivity, temperature, and depth. Data are automatically transmitted back via satellite.  [Learn More](http://www.whoi.edu/itp "Learn More")

## Motivation
Since 2005, 121 ITP systems have been deployed, and more than 130,000 water profiles have been collected. As these data continue to accumulate, and the number of users working with the data increases, the need has become apparent for a set of tools to access, search for, and manipulate ITP data.

## Features
  - Easily and rapidly read from all available ITP profiles
  - Search profiles based on
    - latitude range
    - longitude range
    - date range
    - system number
  - Profiles make available derived values such as depth and potential temperature

## Usage
This is the formal documentation for the ItpQuery and Profile classes. To get started, see the section [An Introduction](#An-Introduction)
### class itp_query.**ItpQuery**

An `ItpQuery` object is used to connect to, and request profiles from, the ITP database. 
`ItpQuery` allows you to specify filter criteria, and then fetch a list of `profile` objects that match the criteria. 

#### Methods
 **\_\_init\_\_**(*db_path[, keyword filters]*)    
You must supply `db_path` -a path to the ITP database. A variety of keyword arguments are accepted: 

Keyword | Description
:--- | :---
latitude | a two element list specifying the Southern and Northern bounding parallels. Acceptable range is [-90 to 90]
longitude | a two element list specifying the Western and Eastern bounding meridians. Acceptable meridian range is [-180 to 180].
date_time | a two element list specifying the start and end time bounds. Times must be specified in Python `datetime`.
system | a list of ITP system numbers to filter for.
pressure | a two element list specifying the range of pressures to return. Note that pressure range only specifies pressure bounds. It does not ensure that a profile will have pressure values up to the bounds.
extra_variables | a list of "extra variables" that must be present in the profiles. If multiple variables are provided, the result will be an OR query (i.e. the results will have at least one of the variables, but not necessarily all). Supported values are: dissolved_oxygen, nacm, vert, east, north, par, turbidity, cdom, chlorophyll_a.

Example:
```
ItpQuery('C:/path/to/itp_db.db', latitude=[75, 80], longitude=[-135, -90])
```
**set_filter_dict**(*filter_dict*)  
Filter arguments can be passed in after instantiation. `set_filter_dict` will overwrite existing filters.
```
from datetime import datetime
filters = {
    'latitude': [60, 90],
    'longitude': [-100 0],
    'system': [1, 2, 3, 4],
    'date_time': [datetime(2010, 1, 1), datetime(2010, 12, 31)]
}
query = ItpQuery('C:/path/to/itp_db.db')
query.set_filter_dict(filters)
```

**add_filter**(*keyword, value*)  
Add filter arguments one at a time. `add_filter` only adds or modifies a single filter and will not affect any other filters if they exist.
```
query = ItpQuery('C:/path/to/itp_db.db')
query.add_filter(latitude=[80, 90])
```

**fetch**()  
Execute a search of the ITP database using the pre-specified filters. Returns 
a list of `Profile` objects that match the search criteria.

**set_max_results**(*n_results*)  
By default, `fetch` is limited to returning 5000 profiles in order to avoid 
protracted wait times and/or memory limitations in the event of an 
overly broad search. The limit is a fail-safe. If you need more profiles, 
call this method before fetch.

### class itp_query.**Profile**
`ItpQuery`'s `fetch` method returns a list of `Profile` objects. Each profile object represents a single profile 
with the following properties:


Property | Description 
:---|:---
date_time | an ISO8601 string representation of the UTC time when the profile began  
latitude  |the latitude where the profile began 
longitude | the longitude where the profile began 
system_number | an integer representing the ITP number 
profile_number | an integer representing the profile number 
source | the original filename used to generate the profile in the database 
pressure | a Numpy array (1xN) 
temperature | a Numpy array (1xN) 
salinity | a Numpy array (1xN) 

#### Methods  
The following methods calculate derived values based on the above data. Note: most of these methods utilize the TEOS-10 GSW package.

**potential_temperature**(*p_ref=0*)  
Calculates potential temperature from in-situ temperature.

**height**()  
Calculates height from sea pressure (+ up).

**depth**()  
Calculates depth from sea pressure; simply negative height (+ down).

**python_datetime**()  
Returns the time the profile began as a Python datetime object.

**posix_time**()  
Returns the time the profile began in POSIX time, the number of seconds since
1970-01-01T00:00:00.

**absolute_salinity**()

**conservative_temperature**()

**density**()  

**freezing_temperature_zero_pressure()**  
Conservative Temperature at which seawater freezes at the surface.

**heat_capacity**()  
Calculates the isobaric heat capacity of seawater.


## An introduction
To get started, you need to install the ITP-Python package and download the 
ITP database. Download the itp_final_xxxx.zip database. See the bottom of the page for instructions.

It is very easy to search for ITP profiles based on latitude, longitude, time 
and system number. The following example demonstrates how to find all 
profiles from 2010 in the region bounded by 70 and 80 degrees North, and 
170 to 140 degrees West. Note the order that the bounds are specified: 
Southern, Northern for latitude, and Western, Eastern for longitude.

First import `ItpQuery` from the itp_python package. If you plan to search by date, also import Python's `datetime` module
```
from itp_python.itp_query import ItpQuery
from datetime import datetime
```
Specify the path to the database file you downloaded. Define the start and end times you wish to search for.
```
path = 'c:/path/to/itp_db.db'
time_range = [datetime(2010, 1, 1), datetime(2010, 12, 31)]
```
Create an ItpQuery object, and pass in the path and other optional arguments. Once it's created, call `fetch()` to initiate the search.
```
query = ItpQuery(path, latitude=[70, 80], longitude=[-170, -140], date_time=time_range)
results = query.fetch()
```
ItpQuery will query the database and return all the ITP profiles that fit the search criteria.
```
>>> len(results)
3093
```
In this case, 3093 profiles were returned. The returned profiles are `Profile` objects. 
```
>>> type(results[0])
<class 'itp_python.itp_query.Profile'>
```
`Profile` objects contain metadata such as the profile's location and time,  as well as the pressure, temperature, and salinity measurements. In addition, the `Profile` object has a series of methods that calculate derived values such as depth and potential temperature. See the documentation above.


## Examples
### Plot salinity vs pressure
Using the first profile returned above
```
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(results[0].salinity, results[0].pressure)
ax.invert_yaxis()
ax.set_xlabel('Salinity')
ax.set_ylabel('Pressure (dbar)')
```
<img src='https://github.com/WHOI-ITP/ITP-Python/raw/master/resources/salinity_vs_pressure.PNG' width='400'/>

### Plot a drift track for ITP1
```
from mpl_toolkits.basemap import Basemap

results = ItpQuery('c:/path/to/itp_db.db', system=[1]).fetch()
longitude = [p.longitude for p in results]
latitude = [p.latitude for p in results]
m = Basemap(projection='npstere', boundinglat=70, lon_0=0, resolution='i')
m.drawcoastlines()
m.fillcontinents()
m.drawparallels(range(70, 90, 5))
m.drawmeridians(range(-180,180,20), latmax=85)
m.plot(longitude, latitude, latlon=True)
```
<img src='https://github.com/WHOI-ITP/ITP-Python/raw/master/resources/drift_track.PNG' width='400px'/>

### Create a temperature section of the ITP1 drift track
```
import matplotlib.pyplot as plt
import numpy as np
from itp_python.itp_query import ItpQuery
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
```
<img src='https://github.com/WHOI-ITP/ITP-Python/raw/master/resources/itp1_section.PNG' width='600px'/>

### Show a map with temperature at 400m
The following example shows a scatter plot of the the temperature at 400 meters from all ITPs in the region bounded by 70 and 80 degrees North, and 
180 to 130 degrees West during 2006 and 2007.

```
import numpy as np
import matplotlib.pyplot as plt
from itp_python.itp_query import ItpQuery
from datetime import datetime
from mpl_toolkits.basemap import Basemap


PATH = r'D:\ITP Data\itp_final_2020_09_14.db'
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
```
<img src='https://github.com/WHOI-ITP/ITP-Python/raw/master/resources/scatter_400.PNG' width='500px'/>

## Installation
  1. Install ITP-Python using pip:
 `pip install git+https://github.com/WHOI-ITP/ITP-Python`
  2. Download and unzip the ITP **final** database https://www.dropbox.com/sh/5u68j8h5eiamk1x/AABZTJd3Hx2y-GAsoBKyZo01a?dl=0
  3. To plot data, install matplotlib `pip install matplotlib`
  4. To plot geographic data on a map, you need to install basemap for matplotlib. If using
  Windows, visit https://www.lfd.uci.edu/~gohlke/pythonlibs/#basemap for a 
  precompiled binary. Download, then install using pip.
