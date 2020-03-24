
import sqlite3
import os
import Weibo
import datetime

DB_DIRECTORY = os.path.join(\
    os.path.split(os.path.realpath(__file__))[0], "../database/")
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

def commit():
    global _conn
    _conn.commit()

def disconnect():
    global _conn
    global _cursor
    _conn.close()
    _cursor = None
    _conn = None

# [!] remember to commit after operations

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
    results = _cursor.fetchall() # 可优化->fetchone()
    return results

def insert(table, values):
    global _conn
    global _cursor
    _cursor.execute("INSERT INTO {} VALUES {}".format(table, "(" + ",".join(['?' for _ in values]) + ")"),\
                   values)

def insert_if_not_exist(table, values):
    global _conn
    global _cursor
    _cursor.execute("INSERT OR IGNORE INTO {} VALUES {}"\
           .format(table, "(" + ",".join(['?' for _ in values]) + ")"),\
                   values)

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

def read_update_time():
    global _cursor
    _cursor.execute("SELECT value FROM meta WHERE name = ?", ['rumorwords_update_yy'])
    yy = _cursor.fetchone()[0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", ['rumorwords_update_mm'])
    mm = _cursor.fetchone()[0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", ['rumorwords_update_dd'])
    dd = _cursor.fetchone()[0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", ['rumorwords_update_hh'])
    hh = _cursor.fetchone()[0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", ['rumorwords_update_mi'])
    mi = _cursor.fetchone()[0]
    _cursor.execute("SELECT value FROM meta WHERE name = ?", ['rumorwords_update_ss'])
    ss = _cursor.fetchone()[0]
    return datetime.datetime(yy,mm,dd,hh,mi,ss)

def write_update_time():
    global _cursor
    time = datetime.datetime.now()
    _cursor.execute("UPDATE meta SET value = ? WHERE name = ?", (time.year, 'rumorwords_update_yy'))
    _cursor.execute("UPDATE meta SET value = ? WHERE name = ?", (time.month, 'rumorwords_update_mm'))
    _cursor.execute("UPDATE meta SET value = ? WHERE name = ?", (time.day, 'rumorwords_update_dd'))
    _cursor.execute("UPDATE meta SET value = ? WHERE name = ?", (time.hour, 'rumorwords_update_hh'))
    _cursor.execute("UPDATE meta SET value = ? WHERE name = ?", (time.minute, 'rumorwords_update_mi'))
    _cursor.execute("UPDATE meta SET value = ? WHERE name = ?", (time.second, 'rumorwords_update_ss'))

# respond to javascript
def js_respond_search(keyword):
    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    cursor = conn.cursor()

    entry_id_selected = set()
    for i in range(3):
        cursor.execute("SELECT entry_list FROM {0}_lut WHERE {0} = ?".format(['nr', 'ns', 'nt'][i]), (keyword,))
        entry_list_sel = cursor.fetchone()[0].split(';')
        [entry_id_selected.add(str(entry_id)) for entry_id in entry_list_sel]

    return json.dumps(entry_id_selected)

def js_respond_show(entry_id):
    # dict: mid -> Weibo-dict
    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    cursor = conn.cursor()

    # weibo part
    cursor.execute("SELECT weibo_list FROM entries WHERE entry_id = ?", (entry_id,))
    weibo_list = [{'mid': int(weibo_id_str)}\
                  for weibo_id_str in cursor.fetchone()[0].split(';')]

    # look up weibo uid, content, time
    cursor.execute("SELECT uid, content, update_time, dt_id_list FROM weibo WHERE mid = ?", \
                    [weibo_dict['mid'] for weibo_dict in weibo_list])
    weibo_sel = cursor.fetchall()
    uid_lookup = dict()
    for iweibo in range(len(weibo_list)):
        uid = int(weibo_sel[iweibo][0])
        uid_lookup[uid] = ''
        content = weibo_sel[iweibo][1]
        update_time = weibo_sel[weibo][2]
        weibo_list[iweibo]['uid'] = uid
        weibo_list[iweibo]['content'] = content
        weibo_list[iweibo]['update_time'] = update_time

    # uid -> nickname
    cursor.executemany("SELECT nickname FROM user_lut where user_id = ?", list(uid_lookup.keys()))
    nicknames = cursor.fetchall()
    i_nickname = 0
    for uid in uid_lookup.keys():
        uid_lookup[uid] = nicknames[i_nickname]
        i_nickname += 1

    for iweibo in range(len(weibo_list)):
        weibo_list[iweibo]['nickname'] = uid_lookup[weibo_list[iweibo]['uid']]

    # transmission part
    iweibo = 0
    for i_weibo in range(len(weibo_sel)):
        all_trans_id = []

        dt_id_list = [int(dt_id) for dt_id in weibo_sel[iweibo][3].split(';')]
        cursor.executemany("SELECT trans_id FROM date_transmission WHERE dt_id = ?", dt_id_list)
        trans_id_list_list = cursor.fetchall()
        for trans_id_list in trans_id_list_list:
            all_trans_id.extend(trans_id_list.split(';'))

        weibo_list[iweibo]['trans_list'] = [int(trans_id_str) for trans_id_str in all_trans_id]
        iweibo += 1

    return json.dumps(weibo_list)

def js_respond_transmit(trans_id):
    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    cursor = conn.cursor()

    cursor.execute("SELECT uid, content, trans_time FROM transmitted WHERE mid = ?", (trans_id,))
    trans_sel = cursor.fetchone()

    transmitted = dict()
    transmitted['uid'] = trans_sel[0]
    transmitted['content'] = trans_sel[1]
    transmitted['trans_time'] = trans_sel[2]

    cursor.execute("SELECT nickname FROM user_lut WHERE user_id = ?", (transmitted['uid'],))
    transmitted['nickname'] = cursor.fetchone()[0]

    return json.dumps(transmitted)
