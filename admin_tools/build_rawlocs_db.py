import os
import sqlite3
import sys
import time
from admin_tools.rawlocs import RawlocsCollection
from datetime import datetime
from pathlib import Path


def create_empty_db(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    db_connection = sqlite3.connect(path)
    c = db_connection.cursor()
    c.execute(
        ''' 
        CREATE TABLE rawlocs (
            id INTEGER PRIMARY KEY,
            system_number INTEGER,
            date_time TEXT,
            latitude REAL, 
            longitude REAL
        )
        '''
    )
    db_connection.commit()
    db_connection.close()


def write_to_db(c, rawlocs):
    for i in range(len(rawlocs.date_time)):
        c.execute('INSERT INTO rawlocs VALUES (?,?,?,?,?)', (
            None,
            rawlocs.system_number,
            rawlocs.date_time[i],
            rawlocs.latitude[i],
            rawlocs.longitude[i])
        )


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'No input path specified'
    path = Path(sys.argv[1])

    start_time = time.time()
    db_filename = path / ('itp_rawlocs_' +
                          datetime.now().strftime('%Y_%m_%d') + '.db')
    create_empty_db(db_filename)
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    for profile in RawlocsCollection.glob(path):
        write_to_db(cursor, profile)
        print(profile.system_number)
        connection.commit()

    connection.commit()
    connection.close()
    etime = time.time()
    print('Database built in {:0.1f} seconds'.format(etime - start_time))

