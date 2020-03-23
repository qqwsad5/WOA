
import Weibo
import html
import bs4
import hanlp
import Meta

'''parsing weibo'''
def parseRaw(weibo_raw):
    pass
    return mid, nickname, user_id, time, content, trans_source_uid_mid


def parseContent(content_list):
    results = Meta.recognizer([list(content) for content in content_list])

    return nr_list, ns_list, nt_list


def parseTransList(weibo_raw):
    pass
    return []


def init_from(weibo_raw):
    mid, nickname, user_id, time, content, trans_source_uid_mid = parseRaw(weibo_raw)
    nr_list, ns_list, nt_list = parseContent(content)
    weiboDoc = Weibo(mid + "/" + str(user_id),\
                     nickname,\
                     time,\
                     content,\
                     nr_list,\
                     ns_list,\
                     nt_list,\
                     open_weibo(trans_source_uid_mid))

    return weiboDoc


def _solid_news(nr, ns, nt):
    ## 微博的内容量 & 排除无具体内容的微博
    total_weight = Meta.CREDITS[0] * len(nr) + \
                   Meta.CREDITS[1] * len(ns) + \
                   Meta.CREDITS[2] * len(nt)
    if total_weight < Meta.WEIGHT_THRES: return False
    return True


'''web access interface'''
def _open_weibo(source_weibo_uid_mid):
    # assert: this weibo has no transmission
    uid, mid = source_weibo_uid_mid.split('/')
    mid = Meta.url_to_mid(mid)

    return None


'''综合'''
def rumorwords_to_weibo_list(keywords, after_time):
    return []


def test_rumorwords_to_weibo_list():
    weibo_list = []

    content_list = []
    # trasmit
    user_id = 7307216655
    mid = 4485778127905740
    weibo_id = "{}/{}".format(user_id, Meta.mid_to_url(mid))
    pub_time = datetime.datetime(2020, 3, 23, 23, 11, 50)
    content = "崔天凯应该辞职。"
    content_list.append(Weibo.Weibo(weibo_id, ))

    # source
    user_id = 1974576991
    mid = 4485637652277214
    weibo_id = "{}/{}".format(user_id, Meta.mid_to_url(mid))
    pub_time = datetime.datetime(2020, 3, 23, 13, 53, 38)
    content = "【我驻美大使崔天凯回应“病毒来自美国军方实验室”说法】#崔天凯回应病毒来自美国军方说法# 据中国驻美国大使馆官网消息，3月17日，崔天凯大使接受AXIOS和HBO联合节目的采访，就新冠肺炎疫情等回答了记者乔纳森·斯旺的提问。"

    parseContent(content)

    trans = Weibo.Weibo(weibo_id, pub_time, content, nr, ns, nt, trans_source)
    return []


def get_trans_list(source_weibo_uid_mid, time_after):
    weibo_raw = _open_weibo(source_weibo_uid_mid)
    trans_list = parseTransList(weibo_raw)
    pass # 过滤掉 time_after 之前的转发
    return []
