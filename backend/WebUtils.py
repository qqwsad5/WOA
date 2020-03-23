
import Weibo
import html
import bs4
import Meta
import datetime

'''parsing weibo'''
def parseRaw(weibo_raw):
    pass
    return mid, nickname, user_id, time, content, trans_source_uid_mid


def parseContent(content_list):
    results = Meta.recognizer([list(content) for content in content_list])
    nr_list_list = []
    ns_list_list = []
    nt_list_list = []
    
    for result in results:
        nr_list_list.append(set())
        ns_list_list.append(set())
        nt_list_list.append(set())
        [{'NR': nr_list_list[-1], \
          'NS': ns_list_list[-1], \
          'NT': nt_list_list[-1]}[entity_tuple[1]].add(entity_tuple[0]) \
        for entity_tuple in result]
        nr_list_list[-1] = list(nr_list_list[-1])
        ns_list_list[-1] = list(ns_list_list[-1])
        nt_list_list[-1] = list(nt_list_list[-1])

    return nr_list_list, ns_list_list, nt_list_list
    # each nx_list_list is N x ?, ? is numebr of nx entities in certain content


def parseTransList(weibo_raw):
    pass
    return []


def _solid_news(nr, ns, nt):
    ## 微博的内容量 & 排除无具体内容的微博
    total_weight = Meta.CREDITS[0] * len(nr) + \
                   Meta.CREDITS[1] * len(ns) + \
                   Meta.CREDITS[2] * len(nt)
    if total_weight < Meta.WEIGHT_THRES: return False
    return True


'''web access interface'''
def _open_weibo(mid):
    # assert: this weibo has no transmission
    return None


'''综合'''
def rumorwords_to_weibo_list(keywords, after_time):
    return []


def test_rumorwords_to_weibo_list():
    weibo_list = []

    content_list = []
    
    # source
    uid = 1974576991
    mid = 4485637652277214
    nickname = "环球时报"
    pub_time = datetime.datetime(2020, 3, 23, 13, 53, 38)
    content = "【我驻美大使崔天凯回应“病毒来自美国军方实验室”说法】#崔天凯回应病毒来自美国军方说法# 据中国驻美国大使馆官网消息，3月17日，崔天凯大使接受AXIOS和HBO联合节目的采访，就新冠肺炎疫情等回答了记者乔纳森·斯旺的提问。"
    source = Weibo.Weibo(mid, uid, nickname, pub_time, content, [], [], [], None)
    content_list.append(content)
    weibo_list.append(source)

    # trasmit
    uid = 7307216655
    mid = 4485778127905740
    nickname = "我跟你梭哈"
    pub_time = datetime.datetime(2020, 3, 23, 23, 11, 50)
    content = "崔天凯应该辞职。"
    transmit = Weibo.Weibo(mid, uid, nickname, pub_time, content, [], [], [], source)
    content_list.append(content)
    weibo_list.append(transmit)

    nr_list_list, ns_list_list, nt_list_list = parseContent(content_list)
    for i in range(len(weibo_list)):
        weibo_list[i].set_lists((nr_list_list[i], ns_list_list[i], nt_list_list[i]))

    return weibo_list


def get_trans_list(mid, time_after):
    weibo_raw = _open_weibo(mid)
    trans_list = parseTransList(weibo_raw)
    pass # 过滤掉 time_after 之前的转发
    return []
