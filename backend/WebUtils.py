
import Weibo
import html
import bs4
import hanlp


'''parsing weibo'''
def parseRaw(weibo_raw):
    pass
    return mid, user_id, time, content, trans_source_uid_mid


def parseContent(content):
    pass
    return nr_list, ns_list, nt_list


def parseTransList(weibo_raw):
    pass
    return []


def init_from(weibo_raw):
    mid, user_id, time, content, trans_source_uid_mid = parseRaw(weibo_raw)
    nr_list, ns_list, nt_list = parseContent(content)
    weiboDoc = Weibo(mid + "/" + str(user_id),\
                     time,\
                     content,\
                     nr_list,\
                     ns_list,\
                     nt_list,\
                     open_weibo(trans_source_uid_mid))

    return weiboDoc


'''web access interface'''
def open_weibo(source_weibo_uid_mid):
    # assert: this weibo has no transmission
    pass
    return None


'''综合'''
def rumorwords_to_weibo_list(keywords, after_time):
    pass


def get_trans_list(source_weibo_uid_mid, time_after):
    weibo_raw = open_weibo(source_weibo_uid_mid)
    trans_list = parseTransList(weibo_raw)
    pass # 过滤掉 time_after 之前的转发
    return []
