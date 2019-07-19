import sqlite3
from pathlib import Path
from itp_python.file_parsing import parse_itp_final
import os


"""
This module will build an SQLite database from itp_final profiles.
Unzip the itpXfinal.zip folders, and point PATH to the containing folder
"""


def setup_db(path):
    os.remove('itp.db')
    connection = sqlite3.connect(path)
    c = connection.cursor()
    c.execute(
        ''' 
        CREATE TABLE profiles (
            id INTEGER PRIMARY KEY,
            system_number INTEGER,
            profile_number INTEGER,
            file_name TEXT,
            date_time TEXT,
            latitude REAL, 
            longitude REAL,
            n_depths INTEGER
        )
        '''
    )

    c.execute(
        ''' 
        CREATE TABLE ctd (
            id INTEGER PRIMARY KEY,
            profile_id INT,
            pressure INT, 
            temperature INT, 
            salinity INT,
            nobs INT
        )
        '''
    )

    c.execute(
        ''' 
        CREATE TABLE other_variables (
            ctd_id INTEGER,
            variable_id INTEGER, 
            value REAL
        )
        '''
    )

    c.execute(
        ''' 
        CREATE TABLE variables (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            precision INT,
            units TEXT
        )
        '''
    )

    c.execute(
        '''
        CREATE INDEX idx_profile_id ON ctd(profile_id)
        '''
    )

    c.execute(
        '''
        CREATE INDEX idx_variable_name_pid
        ON other_variables(ctd_id)
        '''
    )

    connection.commit()
    connection.close()


def write_to_db(path, itp_profile):
    connection = sqlite3.connect(path)
    c = connection.cursor()
    c.execute('INSERT INTO profiles VALUES (?,?,?,?,?,?,?,?)', (
        None,
        itp_profile.metadata('system_number'),
        itp_profile.metadata('profile_number'),
        itp_profile.metadata('file_name'),
        itp_profile.metadata('date_time'),
        itp_profile.metadata('latitude'),
        itp_profile.metadata('longitude'),
        itp_profile.metadata('n_depths'))
    )
    rowid = c.lastrowid
    variables = ['pressure', 'temperature', 'salinity', 'nobs']
    scaled_values = {v: itp_profile.scaled_data(v) for v in variables}
    for i in range(itp_profile.metadata('n_depths')):
        c.execute('INSERT INTO ctd VALUES (?,?,?,?,?,?)', (
            None,
            rowid,
            scaled_values['pressure'][i],
            scaled_values['temperature'][i],
            scaled_values['salinity'][i],
            scaled_values['nobs'][i])
        )

    # other_sensors = set(itp.active_sensors()) - set(REQUIRED_SENSORS)
    # if other_sensors:
    #     ctd_id = c.execute('SELECT id FROM ctd '
    #                        'WHERE profile_id = ? '
    #                        'ORDER BY id', (rowid,)).fetchall()
    #     for sensor in other_sensors:
    #         assert len(ctd_id) == len(itp.data(sensor))
    #         c.execute('INSERT OR IGNORE INTO sensor_names VALUES (?,?)',
    #                   (None,sensor))
    #         sensor_id = c.execute('SELECT id FROM sensor_names WHERE name=?',
    #                               (sensor,)).fetchone()
    #         for i, value in enumerate(itp.data(sensor)):
    #             if value is None:
    #                 continue
    #             sql = 'INSERT INTO other_sensors VALUES ' \
    #                   '(?, ?, ?)'
    #             c.execute(sql, (ctd_id[i][0], sensor_id[0], value))

    connection.commit()
    connection.close()


if __name__ == '__main__':
    setup_db('itp.db')
    # PATH = 'E:/ITP Data/final/'
    PATH = 'E:/ITP Data/final/itp48final/'
    # PATH = 'E:/ITP Data/final/itp1final/'
    files = list(Path(PATH).glob('**/itp*grd*.dat'))
    for file_path in files:
        print(file_path)
        itp_profile = parse_itp_final(file_path)
        write_to_db('itp.db', itp_profile)
