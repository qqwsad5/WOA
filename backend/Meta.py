
'''words that tell a weibo is about rumor'''
KEYWORDS = ['谣言', '辟谣', '网传']

'''after this dates stop collecting weibo's transmissions'''
UPDATE_TRANSMIT_ZONE = 7 # days

'''weights for NR, NS, NT'''
CREDITS = [2, 1, 3]

'''minimum weight for keyword sum'''
WEIGHT_THRES = 5

'''sleep time until next search / update of database'''
SLEEP_SEARCH = 5
SLEEP_UPDATE = 24*60*60


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

URL_TEMPLATE = "https://m.weibo.cn/api/container/getIndex?type=wb&queryVal={}&containerid=100103type=2%26q%3D{}&page={}"
SEARCH_PAGES = 2

NEW_TRANSMIT_PAGES = 5


def _base62_encode(num, alphabet=ALPHABET):
    if (num == 0): return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def _base62_decode(string, alphabet=ALPHABET):
    base = len(alphabet)
    strlen = len(string)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
    return num

def mid_to_url(midint):
    midint = str(midint)[::-1]
    size = len(midint) // 7 if len(midint) % 7 == 0 else len(midint) // 7 + 1
    result = []
    for i in range(size):
        s = midint[i * 7: (i + 1) * 7][::-1]
        s = _base62_encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4: s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)

def url_to_mid(url):
    url = str(url)[::-1]
    size = len(url) // 4 if len(url) % 4 == 0 else len(url) // 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(_base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7: s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))

import datetime
def fromisoformat(string):
    if type(string) == datetime.datetime: return string
    return datetime.datetime(int(string[:4]), int(string[5:7]), int(string[8:10]), \
                             int(string[11:13]), int(string[14:16]), int(string[17:19]))


import hanlp
global recognizer
recognizer = None

def load_hanlp_recognizer():
    global recognizer
    if recognizer == None:
        recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)

def unload_hanlp_recognizer():
    global recognizer
    recognizer = None
