# Downloading data and building a database
This is an administrative process and is not necessary for most users. Pre-built databases are available.

## Download data files
From the command line, enable venv. Navigate to admin_tools directory.

```
python download_itp_files.py C:/data/path/
```

The software will download all the latest itp files from WHOI's FTP server and unzip them to the specified path. If there are already ITP files in the directory, the software will only download files that have changed since last time. Specify a root data path. For example, don't specify `D:/itp_data/final` Instead use `D:/itp_data` The software will automatically create the `final` folder. Also note, if your path contains a space, the path must be enclosed in double quotes.

## Build the database
Specify the directory from the last step when building the database. Specify the product you would like to build. The supported types are `final`, `cormat`, `grid`, `raw`

**Important!** final and grid data have the same file signature `**/itp*grd*.dat` Therefore you must specify the subdirectory the desired data resides. Otherwise both data types could be added to the database. 
```
python -m admin_tools.database "D:/Itp Data/final"
```