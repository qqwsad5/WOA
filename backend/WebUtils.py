import Weibo
import Meta
import Database

import html
import bs4
import datetime
import copy
import os
import re
import requests
import json
import time


JSON_DIRECTORY = os.path.join(\
    os.path.split(os.path.realpath(__file__))[0], "../database/")
JSON_NAME = "weibo_list.json"


global phone_number
phone_number = ""
global password
password = ""
global session
session = None

def release_session():
    global session
    session = None


'''parsing weibo'''
def parseContent(content_list):
    input_list = []
    index_list = []
    count = 0
    for content in content_list:
        split = content.replace('，',' ')\
                   .replace('。',' ')\
                   .replace('！', ' ')\
                   .replace('？', ' ')\
                   .replace('…', ' ').split()
        splits = len(split)
        input_list.extend(split)
        index_list.extend([count for _ in range(splits)])
        count += 1

    BS = 20
    batches = [input_list[BS*b:BS*(b+1)] for b in range(len(input_list) // BS + 1)]

    results = []
    ibatch = 0
    for batch in batches:
        print("batch {} of batches {}".format(ibatch, len(batches)))
        results.extend( Meta.recognizer(\
            [list(batch_content) for batch_content in batch])
        )
        ibatch += 1

    nr_list_list = [set() for _ in range(len(content_list))]
    ns_list_list = [set() for _ in range(len(content_list))]
    nt_list_list = [set() for _ in range(len(content_list))]

    for iresult in range(len(results)):
        result = results[iresult]
        [{'NR': nr_list_list[index_list[iresult]], \
          'NS': ns_list_list[index_list[iresult]], \
          'NT': nt_list_list[index_list[iresult]]}[entity_tuple[1]].add(entity_tuple[0]) \
        for entity_tuple in result]

    nr_list_list = [list(nr_list) for nr_list in nr_list_list]
    ns_list_list = [list(ns_list) for ns_list in ns_list_list]
    nt_list_list = [list(nt_list) for nt_list in nt_list_list]
    return nr_list_list, ns_list_list, nt_list_list
    # each nx_list_list is N x ?, ? is numebr of nx entities in certain content


def _solid_news(nr, ns, nt):
    ## 微博的内容量 & 排除无具体内容的微博
    total_weight = Meta.CREDITS[0] * len(nr) + \
                   Meta.CREDITS[1] * len(ns) + \
                   Meta.CREDITS[2] * len(nt)
    if total_weight < Meta.WEIGHT_THRES: return False
    return True


# referenced from
def _clean_text(text):
    """清除文本中的标签等信息"""
    dr = re.compile(r'(<)[^>]+>', re.S)
    dd = dr.sub('', text)
    dr = re.compile(r'#[^#]+#', re.S)
    dd = dr.sub('', dd)
    dr = re.compile(r'@[^ ]+ ', re.S)
    dd = dr.sub('', dd)
    return dd.strip()

months = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

def _weibotime_to_datetime(weibo_time):
    # like this: 'Mon Apr 06 00:52:34 +0800 2020'
    matcher = re.compile("[A-Za-z]{3} ([A-Za-z]{3}) ([0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2}) \+[0-9]{4} ([0-9]{4})")
    format_string = matcher.match(weibo_time)
    month = months[format_string.group(1)]
    date = format_string.group(2)
    time = format_string.group(3)
    year = format_string.group(4)
    timestring = "{}-{}-{} {}".format(year, month, date, time)
    return datetime.datetime.fromisoformat(timestring)


'''web access interface'''
def _open_weibo(mid):
    # assert: this weibo has no transmission
    # mid, uid, nickname, pub_time, content, trans_source_mid
    url = 'https://m.weibo.cn/detail/{}'.format(mid)
    weibo_dict = dict()

    html = requests.get(url)
    soup = bs4.BeautifulSoup(html.text, "html.parser")
    try:
        main_script = soup.findAll('script')[1]
        render_data = re.findall("var \$render_data =(.+?);\n", main_script.text, re.S)[0][:-9]
        json_data = json.loads(render_data)
    except:
        print("mid: {} is invalid???".format(mid))
        return

    weibo_dict['mid'] = mid
    weibo_dict['uid'] = json_data[0]['status']['user']['id']
    weibo_dict['nickname'] = json_data[0]['status']['user']['screen_name']
    weibo_dict['pub_time'] = _weibotime_to_datetime(json_data[0]['status']['created_at'])
    weibo_dict['content'] = _clean_text(json_data[0]['status']['text'])
    if 'retweeted_status' in json_data[0]['status']:
        weibo_dict['trans_source_mid'] = int(json_data[0]['status']['retweeted_status']['mid'])
    else:
        weibo_dict['trans_source_mid'] = -1

    return weibo_dict


# https://blog.csdn.net/xiaopang123__/article/details/79001426
def _get_trans_mid_list(mid):
    weibo_cn_url = "https://weibo.cn/repost/{}".format(Meta.mid_to_url(mid))
    login_url = r'https://passport.weibo.cn/sso/login'

    global phone_number
    global password
    global session

    if session == None:
        data={'username':phone_number,
          'password':password,
          'savestate':'1',
          'r':r'',
          'ec':'0',
          'pagerefer':'',
          'entry':'mweibo',
          'wentry':'',
          'loginfrom':'',
          'client_id':'',
          'code':'',
          'qq':'',
          'mainpageflag':'1',
          'hff':'',
          'hfp':''}

        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
                'Accept':'text/html;q=0.9,*/*;q=0.8',
                'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Connection':'close',
                'Referer':'https://passport.weibo.cn/signin/login',
                'Host':'passport.weibo.cn'}

        session = requests.session()
        session.post(url=login_url,data=data,headers=headers)

    ans = []
    matcher = re.compile("^/attitude/([0-9a-zA-Z]+)")
    for page in range(20):
        try:
            print("\tpage {} for mid {}".format(page, mid))
            html = session.get(url=weibo_cn_url+"?page={}".format(page))
            soup = bs4.BeautifulSoup(html.text, "html.parser")
            repost_list = soup.findAll('div', {'class': 'c'})
            # find valid repost href
            for repost in repost_list:
                try:
                    href = repost.find('span').find('a')['href']
                    mid_url = matcher.match(href).group(1)
                    ans.append(Meta.url_to_mid(mid_url))
                except:
                    continue
            time.sleep(Meta.SLEEP_SEARCH)
        except:
            print("\tno more pages for mid {}".format(mid))
            break

    return ans


# refernce: github - weibo_wordcloud repo
def _search_weibo_with_keywords(keywords):
    # search in searching bar
    mids = set()
    for keyword in keywords:
        for page_id in range(Meta.SEARCH_PAGES):
            resp = requests.get(Meta.URL_TEMPLATE.format(keyword, keyword, page_id))
            try:
                card_group = json.loads(resp.text)['data']['cards'][0]['card_group']
            except:
                print("no more cards found")
                break

            print('url：', resp.url, ' --- 条数:', len(card_group))
            for card in card_group:
                mblog = card['mblog']
                mid = int(mblog['id'])
                mids.add(mid)

            time.sleep(Meta.SLEEP_SEARCH)

    return list(mids)


'''综合'''
def rumorwords_to_weibo_list(keywords, after_time):
    # search
    search_pool = _search_weibo_with_keywords(keywords) # a list of mid

    # open each
    # + filter
    weibo_pool = dict()
    for search_mid in search_pool:
        if search_mid in weibo_pool: continue

        weibo_raw = _open_weibo(search_mid)
        if weibo_raw == None: continue
        if weibo_raw['pub_time'] <= after_time: continue
        if weibo_raw['trans_source_mid'] == -1: # raw weibo: add
            weibo_pool[weibo_raw['mid']] = weibo_raw
        else:   # transmit weibo: 
            if weibo_raw['trans_source_mid'] not in search_pool:
                # find raw weibo, open, add to weibo_pool
                original_weibo_raw = _open_weibo(weibo_raw['trans_source_mid'])
                weibo_pool[original_weibo_raw['mid']] = original_weibo_raw
            weibo_pool[weibo_raw['mid']] = weibo_raw

    # analyze entities
    content_list = [weibo_pool[mid]['content'] for mid in weibo_pool.keys()]
    nr_list_list, ns_list_list, nt_list_list = parseContent(content_list)
    iweibo = 0
    for mid in weibo_pool.keys():
        weibo_pool[mid]['nr_list'] = nr_list_list[iweibo]
        weibo_pool[mid]['ns_list'] = ns_list_list[iweibo]
        weibo_pool[mid]['nt_list'] = nt_list_list[iweibo]
        iweibo += 1

    dump_weibo_dict = {}
    # 先从转发视角看，如果 原微博+转发 分量足够，则两者均加入
    for mid in weibo_pool.keys():
        if weibo_pool[mid]['trans_source_mid'] == -1: continue
        else:
            original = weibo_pool[weibo_pool[mid]['trans_source_mid']]
            transmit = weibo_pool[mid]
            comb_nr_list = original['nr_list']
            comb_ns_list = original['ns_list']
            comb_nt_list = original['nt_list']
            comb_nr_list.extend(transmit['nr_list'])
            comb_ns_list.extend(transmit['ns_list'])
            comb_nt_list.extend(transmit['nt_list'])
            if _solid_news(comb_nr_list, comb_ns_list, comb_nt_list):
                dump_weibo_dict[mid] = transmit
                dump_weibo_dict[mid]['pub_time'] = str(dump_weibo_dict[mid]['pub_time'])
                if original['mid'] not in dump_weibo_dict:
                    dump_weibo_dict[original['mid']] = original
                    dump_weibo_dict[original['mid']]['pub_time'] \
                     = str(dump_weibo_dict[original['mid']]['pub_time'])

    # 再从未被遍历的原微博视角看，如果 原微博 分量足够，则两者均加入
    for mid in weibo_pool.keys():
        if weibo_pool[mid]['trans_source_mid'] == -1:
            if mid in dump_weibo_dict: continue
            if _solid_news(weibo_pool[mid]['nr_list'], \
                           weibo_pool[mid]['ns_list'], \
                           weibo_pool[mid]['nt_list']):
                dump_weibo_dict[mid] = weibo_pool[mid]
                dump_weibo_dict[mid]['pub_time'] = str(dump_weibo_dict[mid]['pub_time'])

    json.dump([dump_weibo_dict[mid] for mid in dump_weibo_dict.keys()], \
              open(os.path.join(JSON_DIRECTORY, JSON_NAME), "a+") )
    wh = open(os.path.join(JSON_DIRECTORY, JSON_NAME), "a+")
    wh.write(',')
    wh.close()


def fetch_rumor_weibo_list():
    # fetch raw
    jread = json.loads("[" + open(os.path.join(JSON_DIRECTORY, JSON_NAME)).read()[:-1] + "]") # json list of attr dict
    rumor_weibo_list = jread[0]
    for i in range(1, len(jread)):
        rumor_weibo_list.extend(jread[i])

    # create Weibo objs, trans_source is yet an mid
    rumor_weibo_dict = dict()
    for raw_weibo in rumor_weibo_list:
        rumor_weibo_dict[int(raw_weibo['mid'])] = Weibo.Weibo(\
            int(raw_weibo['mid']), int(raw_weibo['uid']), raw_weibo['nickname'], \
            raw_weibo['pub_time'], raw_weibo['content'], \
            raw_weibo['nr_list'], raw_weibo['ns_list'], raw_weibo['nt_list'], int(raw_weibo['trans_source_mid']))

    # fill source mid
    for mid in rumor_weibo_dict:
        if rumor_weibo_dict[mid].trans_source == -1: continue
        source_weibo = rumor_weibo_dict[rumor_weibo_dict[mid].trans_source]
        rumor_weibo_dict[mid].set_trans_source(source_weibo)

    # clear json storage
    jh = open(os.path.join(JSON_DIRECTORY, JSON_NAME), 'w')
    jh.write("")
    jh.close()

    # return
    return rumor_weibo_dict


def test_rumorwords_to_weibo_list():
    rumor_weibo_list = []

    content_list = []
    
    # source
    uid = 1974576991
    mid = 4485637652277214
    nickname = "环球时报"
    pub_time = datetime.datetime(2020, 3, 23, 13, 53, 38)
    content = "【我驻美大使崔天凯回应“病毒来自美国军方实验室”说法】#崔天凯回应病毒来自美国军方说法# 据中国驻美国大使馆官网消息，3月17日，崔天凯大使接受AXIOS和HBO联合节目的采访，就新冠肺炎疫情等回答了记者乔纳森·斯旺的提问。"
    source = Weibo.Weibo(mid, uid, nickname, pub_time, content, [], [], [], None)
    content_list.append(content)
    rumor_weibo_list.append(source)

    # transmit
    uid = 7307216655
    mid = 4485778127905740
    nickname = "我跟你梭哈"
    pub_time = datetime.datetime(2020, 3, 23, 23, 11, 50)
    content = "崔天凯应该辞职。"
    transmit = Weibo.Weibo(mid, uid, nickname, pub_time, content, [], [], [], source)
    content_list.append(content)
    rumor_weibo_list.append(transmit)

    nr_list_list, ns_list_list, nt_list_list = parseContent(content_list)
    for i in range(len(rumor_weibo_list)):
        rumor_weibo_list[i].set_lists((nr_list_list[i], ns_list_list[i], nt_list_list[i]))

    return rumor_weibo_list


def get_trans_list(mid, new_trans_since):
    trans_mid_list = _get_trans_mid_list(mid)
    transmit_list = []

    for mid in trans_mid_list:
        transmit = _open_weibo(mid)
        if transmit == None: continue
        transmit_list.append(transmit)

    contents = [t['content'] for t in transmit_list]
    nr_list, ns_list, nt_list = parseContent(contents)

    iweibo = 0
    trans_Weibo_list = []
    for transmit in transmit_list:
        trans_Weibo_list.append(Weibo.Weibo(\
            transmit['mid'], transmit['uid'], transmit['nickname'], \
            transmit['pub_time'], transmit['content'], \
            nr_list[iweibo], ns_list[iweibo], nt_list[iweibo],\
            transmit['trans_source_mid']))
        iweibo += 1

    # 过滤掉 new_trans_since 之前的转发
    return [transmission for transmission in trans_Weibo_list \
            if transmission.pub_time >= datetime.datetime.fromisoformat(new_trans_since)]


if __name__ == '__main__':
    phone_number = ''
    password = ''

    Database.connect()
    Meta.load_hanlp_recognizer()
    while True:
        rumorwords_update_time = Database.read_update_time()

        rumorwords_to_weibo_list(Meta.KEYWORDS, rumorwords_update_time)

        Database.write_update_time()
        Database.commit()

        time.sleep(Meta.SLEEP_SEARCH)

    Meta.unload_hanlp_recognizer()
    Database.disconnect()
