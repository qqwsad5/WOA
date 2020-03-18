'''words that tell a weibo is about rumor'''
KEYWORDS = ['谣言', '辟谣', '网传']

'''after this dates stop collecting weibo's transmissions'''
UPDATE_TRANSMIT_ZONE = 30 # days

'''weights for NR, NS, NT'''
CREDITS = [4, 1, 2]

'''minimum weight for keyword sum'''
WEIGHT_THRES = 4