# ITP-Python
The Ice Tethered Profiler is an autonomous instrument that vertically profiles the water column under sea ice. The ITP collects measurements of conductivity, temperature, and depth. Data are automatically transmitted back via satellite.  [Learn More](http://www.whoi.edu/itp "Learn More")

## Motivation
Since 2005, 119 ITP systems have been deployed, and more than 120,000 water profiles have been collected. As these data continue to accumulate, and the number of users working with the data increases, the need has become apparent for a set of tools to access, search for, and manipulate ITP data.

## Features
  - Easily and rapidly read from all available ITP profiles
  - Search profiles based on
    - latitude range
    - longitude range
    - date range
    - system number
  - Profiles are returned as a list

## Usage
### class itp_query.**ItpQuery**

An `ItpQuery` object is used to connect to, and request profiles from, the ITP database. 
`ItpQuery` allows you to specify filter criteria, and then fetch a list of `profile` objects that match the criteria. 

#### Methods
 **\_\_init\_\_**(*db_path[, keyword filters]*)    
You must supply `db_path` -a path to the ITP database. A variety of keyword arguments are accepted. 

Keyword | Description
:--- | :---
latitude | a two element list specifying the Southern and Northern bounding parallels. Acceptable range is [-90 to 90]
longitude | a two element list specifying the Western and Eastern bounding meridians. Acceptable meridian range is [-180, 180].
date_time | a two element list specifying the start and end times of the search. Times must be specified in Python `datetime`.
system | a list of ITP system numbers to filter for.

```
query = ItpQuery('C:/path/to/itp_db.db', latitude=[75, 80], longitude=[-135, -90])
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
Add filter arguments one at a time. `add_filter` will not overwrite other filters.
```
query = ItpQuery('C:/path/to/itp_db.db')
query.add_filter(latitude=[80, 90])
```

**fetch**()  
Execute a search of the ITP database using the pre-specified filters.

**set_max_results**(*n_results*)  
By default, `fetch` is limited to returning 5000 profiles in order to avoid 
protracted wait times and/or memory limitations in the event of an 
overly broad search. 


### class itp_query.**Profile**
`ItpQuery`'s `fetch` method returns a list of `Profile` objects. Each profile object represents a single profile 
with the following properties:


Property | Description 
:---|:---
date_time | an ISO8601 representation of the time when the profile began 
latitude  |the latitude where the profile began 
longitude | the longitude where the profile began 
system_number | an integer representing the ITP number 
profile_number | an integer representing the profile number 
source | the original filename used to generate the profile in the database 
pressure | a Numpy array (1xN) 
temperature | a Numpy array (1xN) 
salinity | a Numpy array (1xN) 

#### Example Usage
Return all profiles bounded by the parallels 70 and 80 degrees, the meridians -170 and -140 degrees, during the year 2010. Pass in the arguments using the constructor.
```
from itp_python.itp_query import ItpQuery
from datetime import datetime

path = 'c:/path/to/itp_db.db'
startTime = datetime(2010, 1, 1)
endTime = datetime(2010, 12, 31)

# Create an ItpQuery object and load arguments through the constructor
query = ItpQuery(path, latitude=[70, 80], longitude=[-170, -140], date_time=[startTime, endTime])
# Call fetch to retrieve results
results = query.fetch()
print('{} results returned'.format(len(results)))
```
```
623 results returned
```
Continuing with the data from above, plot salinity vs pressure for the first 
profile.
```
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(results[0].salinity, results[0].pressure)
ax.invert_yaxis()
ax.set_xlabel('Salinity')
ax.set_ylabel('Pressure (dbar)')

```
<img src='https://github.com/WHOI-ITP/ITP-Python/raw/master/resources/salinity_vs_pressure.PNG' width='400'/>

Plot a drift track for ITP1
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

## Installation
  1. Install ITP-Python using pip:
 `pip install git+https://github.com/WHOI-ITP/ITP-Python`
  2. Download and unzip the ITP database https://www.dropbox.com/sh/hrqfe8y2difdn2f/AADGVhBwkCcS4ZxN8s8GmZmma?dl=0
  3. To plot data, install matplotlib `pip install matplotlib`
  4. To plot geographic data on a map, you need to install basemap for matplotlib. If using
  Windows, visit https://www.lfd.uci.edu/~gohlke/pythonlibs/#basemap for a 
  precompiled binary. Download, then install using pip.

