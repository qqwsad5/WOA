
class WeiboRaw: # a bs4 object?
    def __init__(self):
        pass

class Weibo:
    def __init__(self, weibo_id, pub_time, content, nr, ns, nt, trans_source):
        self._weibo_id = weibo_id
        self._pub_time = pub_time
        self._content = content
        self._nr = nr
        self._ns = ns
        self._nt = nt
        self._trans_source = trans_source # another Weibo object

    @property
    def weibo_id(self):
        return self._weibo_id

    @property
    def pub_time(self):
        return self._pub_time
    
    @property
    def content(self):
        return self._content
    
    @property
    def trans_source(self):
        return self._trans_source

    @property
    def name_entities(self):
        return self._nr, self._ns, self._nt

