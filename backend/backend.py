
import update
import time
import Meta
import os
import time
import WebUtils
import Database
import time

if __name__ == '__main__':
    phone_number = '13716393192'
    password = 'dadaliao980308'
    
    Database.connect()
    print("hanlp model load success")
    Meta.load_hanlp_recognizer()

    iters_before_find_repost = Meta.SLEEP_UPDATE // Meta.SLEEP_SEARCH
    while True:
        rumorwords_update_time = Database.read_update_time()

        WebUtils.rumorwords_to_weibo_list(Meta.KEYWORDS, rumorwords_update_time)

        Database.write_update_time()
        Database.commit()

        time.sleep(Meta.SLEEP_SEARCH)
        
        iters_before_find_repost -= 1
        if iters_before_find_repost == 0:
            update.update_db()
            iters_before_find_repost = Meta.SLEEP_UPDATE // Meta.SLEEP_SEARCH

    Meta.unload_hanlp_recognizer()
    Database.disconnect()
