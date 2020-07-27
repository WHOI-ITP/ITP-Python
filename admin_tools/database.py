import os
import sqlite3
import sys
import time
from admin_tools.cormat import CormatCollection
from admin_tools.grid import ITPGridCollection
from admin_tools.itp import REQUIRED_VARIABLES
from admin_tools.itp_final import ITPFinalCollection
from admin_tools.raw import RawCollection
from admin_tools.wod_csv import WODCollection
from datetime import datetime
from pathlib import Path


PRODUCTS = {
    'final': ITPFinalCollection,
    'cormat': CormatCollection,
    'grid': ITPGridCollection,
    'raw': RawCollection
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
            longitude REAL
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
    c.execute('INSERT INTO profiles VALUES (?,?,?,?,?,?,?)', (
        None,
        itp_profile.metadata('system_number'),
        itp_profile.metadata('profile_number'),
        itp_profile.metadata('source'),
        itp_profile.metadata('date_time'),
        itp_profile.metadata('latitude'),
        itp_profile.metadata('longitude'))
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


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'No input path specified'
    path = Path(sys.argv[1])
    product_arg = 'final'
    if len(sys.argv) > 2:
        product_arg = sys.argv[2]
        assert product_arg in PRODUCTS.keys(), 'Invalid product type'

    product = PRODUCTS[product_arg]

    start_time = time.time()
    db_filename = path / ('itp_' + product_arg + '_' + datetime.now().strftime('%Y_%m_%d') + '.db')
    # import pdb; pdb.set_trace()
    create_empty_db(db_filename, include_bio=True)
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    for i, profile in enumerate(product.glob(path)):
        write_to_db(cursor, profile)
        if i % 1000 == 0:
            print(i)
            connection.commit()

    connection.commit()
    connection.close()
    etime = time.time()
    print('Database built in {:0.1f} seconds'.format(etime - start_time))

