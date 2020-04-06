
import Weibo
import Meta
import Database
import numpy as np
import datetime
import WebUtils


def _overlap(list1, list2):
    count = np.sum([1 for kw in list2 if kw in list1])
    return count

def _same_day(date, date_time):
    if date.year  == date_time.year and \
       date.month == date_time.month and \
       date.day  == date_time.day:
        return True
    return False

def _format_as_datetime(datetime_obj):
    return str(datetime_obj)[:19]

def _insert_new_weibo(weibo, nr, ns, nt):
    Database.connect()

    ## 涉及关键词的条目
    nx = ['nr', 'ns', 'nt']
    entries_id = set()
    for i in range(3):
        entries_nx = Database.select_many(nx[i] + '_lut', columns=['entry_list'], \
                                           where={nx[i] + ' = ?': [nr, ns, nt][i]})
        for entry in entries_nx:
            entry_ids = [int(entry_id) for entry_id in entry[0].split(';')]
            entries_id = entries_id.union(set(entry_ids))

    entries = Database.select_many('entries', columns=['nr_list', 'ns_list', 'nt_list', 'weibo_list'],\
                                  where={'entry_id = ?': list(entries_id)})

    ## 找出最佳匹配 entry: bestmatch
    bestmatch = None
    bestscore = 0
    bestmatch_weight = 0
    total_weight = Meta.CREDITS[0] * len(nr) + \
                   Meta.CREDITS[1] * len(ns) + \
                   Meta.CREDITS[2] * len(nt)
    for entry in entries:
        entry_nr = [kw for kw in entry[0].split(';')]
        entry_ns = [kw for kw in entry[1].split(';')]
        entry_nt = [kw for kw in entry[2].split(';')]
        matchscore = Meta.CREDITS[0] * _overlap(entry_nr, nr) + \
                     Meta.CREDITS[1] * _overlap(entry_ns, ns) + \
                     Meta.CREDITS[2] * _overlap(entry_nt, nt)
        weight = Meta.CREDITS[0] * len(entry_nr) + \
                 Meta.CREDITS[1] * len(entry_ns) + \
                 Meta.CREDITS[2] * len(entry_nt)

        # 匹配数更高：喜新厌旧
        if (bestscore < matchscore) or \
           (bestscore == matchscore and bestmatch_weight > weight): # 匹配数相同但新匹配关键词少更简洁：喜新厌旧
            bestmatch = entry
            bestscore = matchscore
            bestmatch_weight = weight

    ## 更新数据库: entries(insert -> nx_lut(update) /update), weibo(insert)
    if bestmatch == None or bestscore <= .5 * total_weight:
        ### ns, nt, nr, weibo -> entries (insert)
        entry_count = Database.select('meta', columns=['value'], where={'name = ?': 'entry_count'})[0][0]
        Database.insert('entries', values= [entry_count, \
                                            ';'.join(nr), \
                                            ';'.join(ns), \
                                            ';'.join(nt), \
                                            str(weibo.mid)])
        
        ### ns, nt, nr, entry_count -> nx_lut(update)
        nx_name = ['nr', 'ns', 'nt']
        for i in range(3):
            for keyword in [nr, ns, nt][i]:
                nx_line = Database.select(nx_name[i]+'_lut', columns=['entry_list'], where={nx_name[i] + " = ?": keyword})
                if len(nx_line) == 0:
                    Database.insert(nx_name[i]+'_lut', values=[keyword, str(entry_count)])
                else:
                    old_entry_list = nx_line[0][0]
                    Database.update(nx_name[i]+'_lut', values={'entry_list': old_entry_list+';'+str(entry_count)}, \
                                                  where={nx_name[i] + "= ?": keyword})

        entry_count += 1
        Database.update('meta', values={'value': entry_count}, where={'name = ?': 'entry_count'})
    else:
        entry_weibo_list = [int(x) for x in bestmatch[3].split(';')]
        if weibo.mid not in entry_weibo_list:
            Database.update('entries', values={'weibo_list': bestmatch[3]+';'+str(weibo.mid)}, \
                                       where={'entry_id = ?': bestmatch[0]})

            Database.insert('weibo', values = [weibo.mid,\
                                               weibo.uid,\
                                               str(weibo.pub_time), \
                                               weibo.content, \
                                               "",\
                                               str(weibo.pub_time)])

            Database.insert_if_not_exist('user_lut', values=[weibo.uid, weibo.sender_nickname])


def _insert_new_transmit(weibo):
    repost_sel = Database.select('transmitted', ['mid'], {"mid = ?": weibo.mid})
    if len(repost_sel) > 0: return
    ## 经过前面的插入/跳过操作，原 weibo 已经在 table: weibo 中了
    try:
        source_mid = weibo.trans_source.mid
    except:
        source_mid = weibo.trans_source

    dt_id_list_sel = Database.select('weibo', columns=['dt_id_list'], where={'mid = ?': source_mid})
    assert(len(dt_id_list_sel) > 0)

    ## 查对dt_id_list
    dt = None
    if len(dt_id_list_sel[0][0]) > 0:
        dt_id_list = [int(x) for x in dt_id_list_sel[0][0].split(';')]
        date_transmission = Database.select_many('date_transmission', columns=['dt_id', 'dt_date', 'trans_id'], \
                                             where={'dt_id = ?': dt_id_list})

        for dt in date_transmission:
            print(dt[1], weibo.pub_time)
            if _same_day(datetime.datetime.strptime(dt[1], '%Y-%m-%d %H:%M:%S'), weibo.pub_time):
                break

    if dt == None:
        # 插入新的 dt line 到 date_transmission table 中
        dt_count = Database.select('meta', columns=['value'], where={'name = ?': 'dt_count'})[0][0]
        Database.update('weibo', values={'dt_id_list': str(dt_count)}, where={'mid = ?': source_mid})
        date = datetime.datetime(weibo.pub_time.year, weibo.pub_time.month, weibo.pub_time.day)
        Database.insert('date_transmission', values=[dt_count, str(date), str(weibo.mid)])
        dt_count += 1
        Database.update('meta', values={'value': dt_count}, where={'name = ?': 'dt_count'})
    else:
        Database.update('date_transmission', values={'trans_id': dt[2]+";"+str(weibo.mid)}, where={"dt_id = ?": dt[0]})

    # 插入新的 transmitted 表项
    Database.insert_if_not_exist('transmitted', values=[weibo.mid, weibo.uid, weibo.content, str(weibo.pub_time)])

    Database.insert_if_not_exist('user_lut', values=[weibo.uid, weibo.sender_nickname])

''' public methods here '''
def create_fake_data():
    Database.connect()
    uid = 1686546714
    nickname = "环球网"
    mid = Meta.url_to_mid('Iz33N9J1h')
    pub_time = datetime.datetime(2020, 3, 17, 18, 28, 0)
    content = "武汉病毒所辟谣石正丽“蚊虫或成第三宿主”言论：从未发布过。"
    nr = ["石正丽"]
    ns = []
    nt = ["武汉病毒所"]
    trans_source = None
    weibo = Weibo.Weibo(mid, uid, nickname, pub_time, content, nr, ns, nt, trans_source)
    _insert_new_weibo(weibo, nr, ns, nt)
    Database.commit()
    Database.disconnect()


def update_db():
    Database.connect()
    # 1: collect new rumors
    rumorwords_weibo_list = WebUtils.test_rumorwords_to_weibo_list() # for test
    # rumorwords_weibo_list = WebUtils.fetch_rumor_weibo_list()

    ## 先考虑非转发的微博
    for related_weibo in rumorwords_weibo_list:

        if related_weibo.trans_source != None:
            ## 通过被转发关系找到的原微博
            weibo = related_weibo.trans_source
            ## 关键词取原微博&转发微博的并集
            nr, ns, nt = weibo.named_entities
            nr_trans, ns_trans, nt_trans = related_weibo.named_entities
            [nr.append(nr_trans_item) for nr_trans_item in nr_trans if nr_trans_item not in nr]
            [ns.append(ns_trans_item) for ns_trans_item in ns_trans if ns_trans_item not in ns]
            [nt.append(nt_trans_item) for nt_trans_item in nt_trans if nt_trans_item not in nt]
        else:
            ## 通过关键词搜索方式找到的原微博
            weibo = related_weibo
            ## 关键词自然是找原微博的 nx
            nr, ns, nt = weibo.named_entities

        _insert_new_weibo(weibo, nr, ns, nt)

    ## 跳过录入过的原微博
    for weibo in rumorwords_weibo_list:
        if weibo.trans_source == None: continue

        _insert_new_transmit(weibo)

    Database.commit()

    # 2: search original weibo, transmit zone update
    today = datetime.datetime.now()
    after_time = today - datetime.timedelta(Meta.UPDATE_TRANSMIT_ZONE)
    original_weibo_list = Database.select(
        'weibo', columns=['mid', 'update_time'], \
        where={"datetime(weibo_time) BETWEEN datetime(?) AND datetime('{}')"\
               .format(_format_as_datetime(datetime.datetime.now())): \
               _format_as_datetime(after_time) })

    for weibo_sel in original_weibo_list:
        mid = weibo_sel[0]
        update_time = weibo_sel[1]
        trans_list = WebUtils.get_trans_list(mid, new_trans_since=update_time)
        for transmission in trans_list:
            # 插入到 date_transmission, transmitted 中
            _insert_new_transmit(transmission)

    WebUtils.release_session()

    Database.commit()
    Database.disconnect()
