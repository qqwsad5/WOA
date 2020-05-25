import os
import WebUtils
import Meta
import Database

def main():
    rumorwords_weibo_dict = WebUtils.fetch_rumor_weibo_list(\
        os.path.join(WebUtils.JSON_DIRECTORY, file))
    print("{} new weibo collected at {}".format(len(rumorwords_weibo_dict), datetime.datetime.now()))

    for mid in rumorwords_weibo_dict:
        try:
            print(mid, rumorwords_weibo_dict[mid].trans_source.mid)
        except:
            print(mid, rumorwords_weibo_dict[mid].trans_source)

    ## 先考虑非转发的微博
    for related_weibo in rumorwords_weibo_dict.values():
        if related_weibo.trans_source != None and related_weibo.trans_source != -1:
            ## 通过被转发关系找到的原微博
            weibo = related_weibo.trans_source
            ## 关键词取原微博&转发微博的并集
            if type(weibo) == int:
                weibo = rumorwords_weibo_dict[weibo]
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

    Database.write_update_time()
    Database.commit()

if __name__ == '__main__':
    Meta.load_hanlp_recognizer()
    main()