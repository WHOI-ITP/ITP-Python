import sqlite3
from pathlib import Path
from itp_python.file_parsing import parse_itp_final


"""
This module will build an SQLite database from itp_final profiles.
Unzip the itpXfinal.zip folders, and point PATH to the containing folder
"""


def setup_db(path):
    connection = sqlite3.connect(path)
    c = connection.cursor()
    c.execute(
        ''' 
        CREATE TABLE profiles (
            system_number INTEGER,
            profile_number INTEGER,
            file_name TEXT,
            date_time TEXT,
            latitude REAL, 
            longitude REAL, 
            channels INTEGER,
            n_depths INTEGER
        )
        '''
    )

    c.execute(
        ''' 
        CREATE TABLE ctd (
            profile_id INTEGER,
            pressure REAL, 
            temperature REAL, 
            salinity REAL, 
            FOREIGN KEY(profile_id) REFERENCES profiles(rowid)
        )
        '''
    )
    connection.commit()
    connection.close()


def write_to_db(path, itp):
    connection = sqlite3.connect(path)
    c = connection.cursor()
    c.execute('INSERT INTO profiles VALUES (?,?,?,?,?,?,?,?)', (
        itp.system_number,
        itp.profile_number,
        itp.file_name,
        itp.date_time,
        itp.latitude,
        itp.longitude,
        len(itp.active_sensors()),
        itp.n_depths)
    )
    rowid = c.lastrowid
    for i in range(itp.n_depths):
        c.execute('INSERT OR IGNORE INTO ctd VALUES (?,?,?,?)', (
            rowid,
            itp.data('pressure')[i],
            itp.data('temperature')[i],
            itp.data('salinity')[i])
        )
    connection.commit()
    connection.close()


if __name__ == '__main__':
    setup_db('itp.db')
    PATH = 'E:/ITP Data/final/'
    files = list(Path(PATH).glob('**/itp*grd*.dat'))
    for file_path in files:
        print(file_path)
        itp_final = parse_itp_final(file_path)
        write_to_db('itp.db', itp_final)
