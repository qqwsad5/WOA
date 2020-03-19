
import sqlite3
import os
import Weibo

DB_DIRECTORY = "./"
DB_NAME = "weibo.db"

def create_db():
    # Open and read the file as a single buffer
    fd = open('init_tables.sql', 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    c = conn.cursor()

    for command in sqlCommands:
        # This will skip and report errors
        try:
            c.execute(command)
        except OperationalError, msg:
            print "Command skipped: ", msg

    conn.commit()
    conn.close()

def select_many(table, columns, where, condition='V'): # condition: 多个where列表时用来表示交际或者并集
    pass

def insert(table, values):
    pass

def select(table, columns, where):
    pass

def update(table, values, where):
    pass

def read_update_time():
    pass

def write_update_time():
    pass

