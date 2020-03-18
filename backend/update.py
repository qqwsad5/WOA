
import Weibo
import Meta
import Database
import numpy as np
import datetime
import WebUtils

def _overlap(list1, list2):
    pass

def _same_day(date, date_time):
    pass

def update_db():
    # 0: mark last update time
    #    update time: 上次按这些关键词搜索时最晚的一条
    rumorwords_update_time = Database.read_update_time()

    # 1: collect new rumors
    rumorwords_weibo_list = WebUtils.rumorwords_to_weibo_list(Meta.KEYWORDS, rumorwords_update_time)
    Database.write_update_time()

    ## 先考虑非转发的微博
    for related_weibo in rumorwords_weibo_list:

        if related_weibo.trans_source != None:
            ## 通过被转发关系找到的原微博
            weibo = related_weibo.trans_source
            might_repeatedly_insert_weibo = True
            ## 关键词取原微博&转发微博的并集
            nr, ns, nt = weibo.named_entities
            nr_trans, ns_trans, nt_trans = related_weibo.named_entities
            nr.extend(nr_trans)
            ns.extend(ns_trans)
            nt.extend(nt_trans)
        else:
            ## 通过关键词搜索方式找到的原微博
            weibo = related_weibo
            might_repeatedly_insert_weibo = False
            ## 关键词自然是找原微博的 nx
            nr, ns, nt = weibo.named_entities

        if might_repeatedly_insert_weibo:
            weibo_sel = Database.select('weibo', columns=['weibo_id'], where={'weibo_id': weibo.weibo_id})
            if len(weibo_sel) > 0: continue

        ## 微博的内容量 & 排除无具体内容的微博
        total_weight = Meta.CREDITS[0] * len(nr) + \
                       Meta.CREDITS[1] * len(ns) + \
                       Meta.CREDITS[2] * len(nt)
        if total_weight < Meta.WEIGHT_THRES: continue

        ## 涉及关键词的条目
        entries = Database.select_many('entries', columns=['entry_id','nr_list','ns_list','nt_list','weibo_list'], \
                                               where={'nr':nr, 'ns':ns, 'nt':nt}, \
                                               condition='V')

        ## 找出最佳匹配 entry: bestmatch
        bestmatch = None
        bestscore = 0
        bestmatch_weight = 0
        for entry in entries:
            matchscore = Meta.CREDITS[0] * _overlap(entry[1], nr) + \
                         Meta.CREDITS[1] * _overlap(entry[2], ns) + \
                         Meta.CREDITS[2] * _overlap(entry[3], nt)
            weight = Meta.CREDITS[0] * len(entry[1]) + \
                     Meta.CREDITS[1] * len(entry[2]) + \
                     Meta.CREDITS[2] * len(entry[3])

            if (bestscore < matchscore) or                              # 匹配数更高：喜新厌旧
               (bestscore == matchscore and bestmatch_weight > weight): # 匹配数相同但新匹配关键词少更简洁：喜新厌旧
                bestmatch = entry
                bestscore = matchscore
                bestmatch_weight = weight


        ## 更新数据库: entries(insert -> nx_lut(update) /update), weibo(insert)
        if bestmatch == None or bestscore <= .5 * total_weight:
            ### ns, nt, nr, weibo -> entries (insert)
            entry_count = Database.select('meta', columns=['value'], where={'name': 'entry_count'})[0][0]
            Database.insert('entries', values= {'entry_id': entry_count, \
                                             'nr_list': ';'.join(nr), \
                                             'ns_list': ';'.join(ns), \
                                             'nt_list': ';'.join(nt), \
                                             'weibo_list': weibo.weibo_id})
            entry_count += 1
            Database.update('meta', values={'value': entry_count}, where={'name': 'entry_count'})
            
            ### ns, nt, nr, entry_count -> nx_lut(update)
            nx = [nr, ns, nt]
            nx_name = ['nr', 'ns', 'nt']
            for i in range(3):
                for keyword in nx[i]:
                    nx_line = Database.select(nx_name[i]+'_lut', columns=['entry_list'], where={nx_name[i]: keyword})
                    if len(nx_line) == 0:
                        Database.insert(nx_name[i]+'_lut', values={'entry_list': str(entry_count), nx_name[i]: keyword})
                    else:
                        old_entry_list = nx_line[0][0]
                        Database.update('entry_list', values={'entry_list': old_entry_list+';'+str(entry_count)}, \
                                                      where={nx_name[i]: keyword})

        else:
            ### bestmatch, weibo -> entries (update)
            Database.update('entries', values={'weibo_list': bestmatch[4]+';'+weibo.weibo_id}, \
                                       where={'entry_id': bestmatch[0]})
            inserted_entry_id = bestmatch[0]

        ### weibo -> weibo (insert)
        Database.insert('weibo', values = {'weibo_id': weibo.weibo_id,\
                                           'weibo_time': weibo.pub_time, \
                                           'content': weibo.content, \
                                           'dt_id_list': "",\
                                           'update_time': weibo.pub_time})

    ## 跳过录入过的原微博
    for weibo in rumorwords_weibo_list:
        if weibo.trans_source == None: continue

        ## 经过前面的插入/跳过操作，原 weibo 已经在 table: weibo 中了
        dt_id_list_sel = Database.select('weibo', columns=['dt_id_list'], where={'weibo_id': weibo.trans_source.weibo_id})
        assert(len(dt_id_sel) > 0)

        ## 查对dt_id_list
        dt_id_list = [int(x) for x in dt_id_list_sel[0][0].split(';')]

        date_transmission = Dataset.select_many('date_transmission', columns=['dt_id', 'dt_date', 'trans_id'], \
                                                 where={'dt_id': dt_id_list})
        
        dt = None
        for dt in date_transmission:
            if _same_day(dt[1], weibo.weibo_time): break

        if dt == None:
            # 插入新的 dt line 到 date_transmission table 中
            pass
        
        # 插入新的 transmitted 表项


    # 2: search original weibo, transmit zone update
    original_weibo_list = Database.select('weibo', columns=['weibo_id', 'update_time'], \
                                          where={'weibo_time > datetime()': str(datetime.datetime(datetime.now() - Meta.UPDATE_TRANSMIT_ZONE))})

    for weibo_sel in original_weibo_list:
        weibo_id = weibo_sel[0]
        update_time = weibo_sel[1]
        trans_list = WebUtils.get_trans_list(weibo_id, update_time)
        for transmission in trans_list:
            # 插入到 date_transmission, transmitted 中
            pass
