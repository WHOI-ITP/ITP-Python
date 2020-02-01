# Downloading data and building a database
This is an administrative process and is not necessary for most users. Pre-built databases are available.

## Download data files
From the command line, enable venv. Navigate to admin_tools directory.

```
python download_itp_files.py C:/data/path/
```

The software will download all the latest itp files from WHOI's FTP server and unzip them tp the specified path. If there are already ITP files in the directory, the software will only download files that have changed since last time.

## Build the database
Specify the directory from the last step when building the database.
```
python build_database.py C:/data/path/
```