# Downloading data and building a database
This step is not necessary for most users. A pre built database can be downloaded from whoi.edu/xxxx

## Download data files
From the command line, enable venv. Navigate to build_database directory.

```
python download_itp_files.py "C:/data/path/"
```

The software will download all the latest itp files and unzip them. If you have done this before, the software will only download files that have changed since last time.

