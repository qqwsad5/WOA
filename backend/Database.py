
import sqlite3
import os
import Weibo
import datetime

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

_conn = None
_cursor = None

def connect():
    _conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    _cursor = conn.cursor()

def disconnect():
    _conn.close()
    _cursor = None
    _conn = None

# remember to commit after operations
# where part has only one argument placeholder
# select_many: argument is a list
def select_many(table, columns, where):
    conditional = where.keys()[0]
    arguments = [(arg,) for arg in where[conditional]] # list of single-arguments
    results = _cursor.executemany("SELECT {} FROM {} WHERE {}"\
                                 .format(','.join(columns), table, conditional),\
                    arguments)

    return results

def select(table, columns, where):
    conditional = where.keys()[0]
    argument = (where[conditional],) # list of single-arguments
    results = _cursor.execute("SELECT {} FROM {} WHERE {}"\
                             .format(','.join(columns), table, conditional),\
                    argument)

    return results

def insert(table, values):
    _cursor.execute("INSERT INTO {} VALUES {}".format(table, "(" + ",".join(['?' for _ in values]) + ")"),\
                   values)
    _conn.commit()

def update(table, values, where):
    columns = values.keys()
    conditional = where.keys()[0]
    argument = [values[column] for column in columns]
    argument.append(where[conditional])

    _cursor.execute("UPDATE {} SET {} WHERE {}".format(\
                        table, \
                        ",".join([column + " = ?" for column in columns]),\
                        conditional),\
                    argument)
    _conn.commit()

def read_update_time():
    yy = _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_yy')[0][0]
    mm = _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_mm')[0][0]
    dd = _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_dd')[0][0]
    hh = _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_hh')[0][0]
    mi = _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_mi')[0][0]
    ss = _cursor.execute("SELECT value FROM meta WHERE name = ?", 'rumorwords_update_ss')[0][0]
    return datatime.datatime(yy,mm,dd,hh,mi,ss)

def write_update_time():
    time = datetime.now()
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_yy', time.year))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_mm', time.month))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_dd', time.day))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_hh', time.hour))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_mi', time.minute))
    _cursor.execute("INSERT INTO meta VALUES (?,?)", ('rumorwords_update_ss', time.second))
    _conn.commit()

