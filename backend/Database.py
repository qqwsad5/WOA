
import sqlite3
import os
import Weibo
import datetime

DB_DIRECTORY = "../database/"
DB_NAME = "weibo.db"

def create_db():
    # Open and read the file as a single buffer
    fd = open('./init_table.sql', 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';;')

    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    c = conn.cursor()

    for command in sqlCommands:
        # This will skip and report errors
        try:
            c.execute(command)
        except Exception as msg:
            print("Command skipped: ", msg)

    conn.commit()
    conn.close()

global _conn
global _cursor

_conn = None
_cursor = None

def connect():
    global _conn
    global _cursor
    _conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    _cursor = _conn.cursor()

def disconnect():
    global _conn
    global _cursor
    _conn.close()
    _cursor = None
    _conn = None

# remember to commit after operations
# where part has only one argument placeholder
# select_many: argument is a list
def select_many(table, columns, where):
    global _cursor
    conditional = list(where.keys())[0]
    arguments = [(arg,) for arg in where[conditional]] # list of single-arguments
    _cursor.executemany("SELECT {} FROM {} WHERE {}"\
                        .format(','.join(columns), table, conditional),\
                        arguments)
    results = _cursor.fetchall()
    return results

def select(table, columns, where):
    global _cursor
    conditional = list(where.keys())[0]
    argument = (where[conditional],) # list of single-arguments
    _cursor.execute("SELECT {} FROM {} WHERE {}"\
                    .format(','.join(columns), table, conditional),\
                    argument)
    results = _cursor.fetchall()
    return results

def insert(table, values):
    global _conn
    global _cursor
    _cursor.execute("INSERT INTO {} VALUES {}".format(table, "(" + ",".join(['?' for _ in values]) + ")"),\
                   values)
    _conn.commit()

def insert_if_not_exist(table, values):
    global _conn
    global _cursor
    print("INSERT OR IGNORE INTO {} VALUES {}".format(table, "(" + ",".join(['?' for _ in values]) + ")"))
    print(values)
    _cursor.execute("INSERT OR IGNORE INTO {} VALUES {}"\
           .format(table, "(" + ",".join(['?' for _ in values]) + ")"),\
                   values)
    _conn.commit()

def update(table, values, where):
    global _conn
    global _cursor
    columns = values.keys()
    conditional = list(where.keys())[0]
    argument = [values[column] for column in columns]
    argument.append(where[conditional])

    _cursor.execute("UPDATE {} SET {} WHERE {}".format(\
                        table, \
                        ",".join([column + " = ?" for column in columns]),\
                        conditional),\
                    argument)
    _conn.commit()

def read_update_time():
    global _cursor
    _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_yy')
    yy = _cursor.fetchall()[0][0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_mm')
    mm = _cursor.fetchall()[0][0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_dd')
    dd = _cursor.fetchall()[0][0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_hh')
    hh = _cursor.fetchall()[0][0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_mi')
    mi = _cursor.fetchall()[0][0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_ss')
    ss = _cursor.fetchall()[0][0]
    return datatime.datatime(yy,mm,dd,hh,mi,ss)

def write_update_time():
    global _conn
    global _cursor
    time = datetime.now()
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_yy', time.year))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_mm', time.month))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_dd', time.day))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_hh', time.hour))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_mi', time.minute))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_ss', time.second))
    _conn.commit()

