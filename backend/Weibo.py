
class Weibo:
    def __init__(self, mid, uid, sender_nickname, pub_time, content, nr, ns, nt, trans_source):
        self._mid = mid
        self._uid = uid
        self._sender_nickname = sender_nickname
        self._pub_time = pub_time
        self._content = content
        self._nr = nr
        self._ns = ns
        self._nt = nt
        self._trans_source = trans_source # another Weibo object

    @property
    def sender_nickname(self):
        return self._sender_nickname

    @property
    def mid(self):
        return self._mid

    @property
    def uid(self):
        return self._uid

    @property
    def pub_time(self):
        return self._pub_time
    
    @property
    def content(self):
        return self._content

    def set_lists(self, lists):
        self._nr, self._ns, self._nt = lists

    def set_trans_source(self, source_weibo):
        self._trans_source = source_weibo
    
    @property
    def trans_source(self):
        return self._trans_source

    @property
    def named_entities(self):
        return self._nr, self._ns, self._nt

