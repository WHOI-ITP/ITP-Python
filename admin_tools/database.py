import os
import sqlite3
import sys
import time
from admin_tools.cormat import CormatCollection
from admin_tools.grid import ITPGridCollection
from admin_tools.itp import REQUIRED_VARIABLES
from admin_tools.itp_final import ITPFinalCollection
from admin_tools.raw import RawCollection
from admin_tools.microcat import ITPMicroCollection
from admin_tools.wod_csv import WODCollection
from datetime import datetime
from pathlib import Path


PRODUCTS = {
    'final': ITPFinalCollection,
    'cormat': CormatCollection,
    'grid': ITPGridCollection,
    'raw': RawCollection,
    'micro': ITPMicroCollection
}


def create_empty_db(path, include_bio=False):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    db_connection = sqlite3.connect(path)
    c = db_connection.cursor()
    c.execute(
        ''' 
        CREATE TABLE profiles (
            id INTEGER PRIMARY KEY,
            system_number INTEGER,
            profile_number INTEGER,
            source TEXT,
            date_time TEXT,
            latitude REAL, 
            longitude REAL,
            direction TEXT
        )
        '''
    )

    c.execute(
        ''' 
        CREATE TABLE ctd (
            id INTEGER PRIMARY KEY,
            profile_id INTEGER,
            pressure INTEGER, 
            temperature INTEGER, 
            salinity INTEGER
        )
        '''
    )

    c.execute(
        '''
        CREATE INDEX idx_profile_id ON ctd(profile_id)
        '''
    )

    if include_bio:
        c.execute(
            ''' 
            CREATE TABLE other_variables (
                ctd_id INTEGER,
                variable_id INTEGER, 
                value INTEGER
            )
            '''
        )

        c.execute(
            ''' 
            CREATE TABLE variable_names (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
            '''
        )

        c.execute(
            ''' 
            CREATE TABLE profile_extra_variables (
                profile_id INTEGER,
                variable_id INTEGER
            )
            '''
        )

        c.execute(
            '''
            CREATE INDEX idx_variable_name_pid
            ON other_variables(ctd_id)
            '''
        )

        c.execute(
            '''
            CREATE INDEX idx_variable_id
            ON profile_extra_variables(variable_id)
            '''
        )

    db_connection.commit()
    db_connection.close()


def write_to_db(c, itp_profile):
    c.execute(
        'INSERT INTO profiles VALUES (?,?,?,?,?,?,?,?)',
        (
            None,
            itp_profile.metadata('system_number'),
            itp_profile.metadata('profile_number'),
            itp_profile.metadata('source'),
            itp_profile.metadata('date_time'),
            itp_profile.metadata('latitude'),
            itp_profile.metadata('longitude'),
            itp_profile.metadata('direction')
        )
    )
    rowid = c.lastrowid
    scaled_values = {v: itp_profile.scaled_data(v) for v in REQUIRED_VARIABLES}
    for i in range(itp_profile.n_samples()):
        c.execute('INSERT INTO ctd VALUES (?,?,?,?,?)', (
            None,
            rowid,
            scaled_values['pressure'][i],
            scaled_values['temperature'][i],
            scaled_values['salinity'][i])
        )

    other_variables = set(itp_profile.variables()) - set(REQUIRED_VARIABLES)
    if other_variables:
        ctd_id = c.execute('SELECT id FROM ctd '
                           'WHERE profile_id = ? '
                           'ORDER BY id', (rowid,)).fetchall()
        for variable in other_variables:
            assert len(ctd_id) == len(itp_profile.data(variable))
            c.execute('INSERT OR IGNORE INTO variable_names VALUES (?,?)',
                      (None, variable))
            sensor_id = c.execute('SELECT id FROM variable_names WHERE name=?',
                                  (variable,)).fetchone()
            c.execute(
                'INSERT OR IGNORE INTO profile_extra_variables VALUES (?,?)',
                (rowid, sensor_id[0]))
            for i, value in enumerate(itp_profile.scaled_data(variable)):
                if value is None:
                    continue
                c.execute('INSERT INTO other_variables VALUES (?, ?, ?)',
                          (ctd_id[i][0], sensor_id[0], value))


def build_database(path, product, include_bio=True):
    path = Path(path)
    collection = PRODUCTS[product]
    start_time = time.time()
    time_str = datetime.now().strftime('%Y_%m_%d')
    db_filename = f'itp_{product}_{time_str}.db'
    create_empty_db(path / db_filename, include_bio)
    connection = sqlite3.connect(path / db_filename)
    cursor = connection.cursor()
    for i, profile in enumerate(collection.glob(path / product)):
        write_to_db(cursor, profile)
        if i % 1000 == 0:
            print(i)
            connection.commit()
    connection.commit()
    connection.close()
    etime = time.time()
    print('Database built in {:0.1f} seconds'.format(etime - start_time))
