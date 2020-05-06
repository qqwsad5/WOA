
import sqlite3
import os
import Weibo
import datetime
import json
import Meta

DB_DIRECTORY = os.path.join(\
    os.path.split(os.path.realpath(__file__))[0], "../database/")
DB_NAME = "weibo.db"
J_NAME = "jounal.db"


def create_db(db_script, db_name):
    # Open and read the file as a single buffer
    fd = open(db_script, 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';;')

    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, db_name))
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
    for args in arguments:
        _cursor.execute("SELECT {} FROM {} WHERE {}"\
                            .format(','.join(columns), table, conditional),\
                            args)
    results = _cursor.fetchall()
    return results


def select(table, columns, where):
    global _cursor
    if len(where) > 0:
        conditional = list(where.keys())[0]
        argument = (where[conditional],) # list of single-arguments
        _cursor.execute("SELECT {} FROM {} WHERE {}"\
                        .format(','.join(columns), table, conditional),\
                        argument)
    else:
        _cursor.execute("SELECT {} FROM {}".format(','.join(columns), table))
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
def _fmt_to_seconds(datetime_obj):
    return str(datetime_obj)[:19]


def js_respond_search(keyword, dump=False):
    # journalize
    conn_journal = sqlite3.connect(os.path.join(DB_DIRECTORY, J_NAME))
    cursor_jounal = conn_journal.cursor()
    
    cursor_jounal.execute("INSERT INTO js_respond_search VALUES (?, ?)",\
        _fmt_to_seconds(datetime.datetime.now()), keyword)
    
    cursor_jounal.execute("SELECT value FROM meta WHERE key = ?", ("search_number",))
    num = cursor_jounal.fetchone()[0]
    cursor_jounal.execute("UPDATE meta SET value = ? WHERE key = ?", (num + 1, "search_number"))
    
    conn_jounal.commit()

    # select
    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    cursor = conn.cursor()

    entry_id_selected = dict()
    for i in range(3):
        cursor.execute("SELECT entry_list FROM {0}_lut WHERE {0} = ?".format(['nr', 'ns', 'nt'][i]), (keyword,))
        sel = cursor.fetchone()
        if sel != None:
            entry_list_sel = [int(x) for x in sel[0].split(';')]
            for entry_id in entry_list_sel:
                if entry_id not in entry_id_selected:
                    nr_sel = cursor.execute("SELECT nr_list FROM entries WHERE entry_id = ?", (entry_id,)).fetchone()[0]
                    ns_sel = cursor.execute("SELECT ns_list FROM entries WHERE entry_id = ?", (entry_id,)).fetchone()[0]
                    nt_sel = cursor.execute("SELECT nt_list FROM entries WHERE entry_id = ?", (entry_id,)).fetchone()[0]

                    if len(nr_sel) > 0: nr_sel = nr_sel.split(';')
                    else: nr_sel = []
                    if len(ns_sel) > 0: ns_sel = ns_sel.split(';')
                    else: ns_sel = []
                    if len(nt_sel) > 0: nt_sel = nt_sel.split(';')
                    else: nt_sel = []
                    print(type(entry_id))
                    entry_id_selected[entry_id] = (nr_sel, ns_sel, nt_sel)

    if dump: json.dump(entry_id_selected, open("./.js_respond_search.json", "w"))
    else:    return json.dumps(entry_id_selected)


def js_respond_show(entry_id, dump=False):
    # jounalize
    conn_journal = sqlite3.connect(os.path.join(DB_DIRECTORY, J_NAME))
    cursor_jounal = conn_journal.cursor()
    cursor_jounal.execute("INSERT INTO js_respond_show VALUES (?, ?)",\
        _fmt_to_seconds(datetime.datetime.now()), entry_id)
    
    cursor_jounal.execute("SELECT value FROM meta WHERE key = ?", ("show_number",))
    num = cursor_jounal.fetchone()[0]
    cursor_jounal.execute("UPDATE meta SET value = ? WHERE key = ?", (num + 1, "show_number"))
    
    conn_jounal.commit()

    # dict: mid -> Weibo-dict
    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    cursor = conn.cursor()

    # weibo_list
    cursor.execute("SELECT weibo_list FROM entries WHERE entry_id = ?", (entry_id,))
    weibo_list = [{'mid': int(weibo_id_str)}\
                  for weibo_id_str in cursor.fetchone()[0].split(';')]

    # look up weibo uid, content, time
    for weibo_dict in weibo_list:
        cursor.execute("SELECT uid, content, update_time, dt_id_list, weibo_time FROM weibo WHERE mid = ?", (weibo_dict['mid'],))
    weibo_sel = cursor.fetchall()

    uid_lookup = dict()
    for iweibo in range(len(weibo_list)):
        uid = int(weibo_sel[iweibo][0])
        uid_lookup[uid] = ''
        content = weibo_sel[iweibo][1]
        update_time = weibo_sel[iweibo][2]
        weibo_time = weibo_sel[iweibo][4]
        weibo_list[iweibo]['uid'] = uid
        weibo_list[iweibo]['content'] = content
        weibo_list[iweibo]['update_time'] = update_time
        weibo_list[iweibo]['weibo_time'] = weibo_time

    # uid -> nickname
    uid_lookup_list = list(uid_lookup.keys())
    for uid in uid_lookup_list:
        cursor.execute("SELECT nickname FROM user_lut where user_id = ?", (uid,))
    nicknames = cursor.fetchall()

    i_nickname = 0
    for uid in uid_lookup.keys():
        uid_lookup[uid] = nicknames[i_nickname]
        i_nickname += 1

    for iweibo in range(len(weibo_list)):
        weibo_list[iweibo]['nickname'] = uid_lookup[weibo_list[iweibo]['uid']]

    # transmission part
    ## stats
    stats = dict()
    ## stats of each transmission
    iweibo = 0
    for i_weibo in range(len(weibo_sel)):
        all_trans_id = []

        dt_id_list = weibo_sel[iweibo][3]
        if len(dt_id_list) > 0:
            for dt_id in dt_id_list.split(';'):
                cursor.execute("SELECT trans_id, dt_date FROM date_transmission WHERE dt_id = ?", (int(dt_id),))
            trans_id_list_list = cursor.fetchall()

            for trans_id_list in trans_id_list_list:
                trans_ids = trans_id_list[0].split(';')
                dt_date = trans_id_list[1]

                if dt_date not in stats: stats[dt_date] = 0
                stats[dt_date] += len(trans_id_str)

                all_trans_id.extend(trans_id_str)

            weibo_list[iweibo]['trans_list'] = [int(trans_id_str) for trans_id_str in all_trans_id]
        else:
            weibo_list[iweibo]['trans_list'] = []

        content = weibo_list[iweibo]['content']
        for keyword in Meta.KEYWORDS:
            if keyword in content: weibo_list[iweibo]['piyao'] = True
            else:                  weibo_list[iweibo]['piyao'] = False

        iweibo += 1

    if dump: json.dump([stats, weibo_list], open("./.js_respond_show.json", "w"))
    else:    return json.dumps([stats, weibo_list])


def js_respond_transmit(trans_id, dump=False):
    conn_journal = sqlite3.connect(os.path.join(DB_DIRECTORY, J_NAME))
    cursor_jounal = conn_journal.cursor()
    cursor_jounal.execute("INSERT INTO js_respond_transmit VALUES (?, ?)",\
        _fmt_to_seconds(datetime.datetime.now()), trans_id)
    
    cursor_jounal.execute("SELECT value FROM meta WHERE key = ?", ("repost_show_number",))
    num = cursor_jounal.fetchone()[0]
    cursor_jounal.execute("UPDATE meta SET value = ? WHERE key = ?", (num + 1, "repost_show_number"))

    conn_jounal.commit()

    conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DB_NAME))
    cursor = conn.cursor()

    cursor.execute("SELECT uid, content, trans_time FROM transmitted WHERE mid = ?", (trans_id,))
    trans_sel = cursor.fetchone()

    transmitted = dict()
    if trans_sel != None:
        transmitted['uid'] = trans_sel[0]
        transmitted['content'] = trans_sel[1]
        transmitted['trans_time'] = trans_sel[2]

        cursor.execute("SELECT nickname FROM user_lut WHERE user_id = ?", (transmitted['uid'],))
        transmitted['nickname'] = cursor.fetchone()[0]

    if dump: json.dump(transmitted, open("./.js_respond_transmit.json", "w"))
    else: return json.dumps(transmitted)
