import sqlite3
import os, sys
from sqlite3.dbapi2 import Connection

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

p = os.path.join(os.path.dirname(__file__))

dbPath = f'{p}/../{Config.DATABASE}'

def getDb() -> Connection: # ensure that this connection will always check foreign keys
    con = sqlite3.connect(dbPath, check_same_thread=False)
    con.execute("PRAGMA FOREIGN_KEYS=ON")
    con.set_trace_callback(print)
    return con

if __name__ == '__main__':
    
    schemaPath = f'{p}/meedikal.sql'

    if os.path.exists(dbPath):
        os.remove(dbPath)

    schema = open(schemaPath, 'r').read()

    db = getDb()
    cursor = db.cursor()

    cursor.executescript(schema)

    db.commit()