
import update
import time
import Meta
import os
import time

if __name__ == '__main__':
    # os.system("python3 {}".format(\
    #     os.path.join(os.path.split(os.path.realpath(__file__))[0], "WebUtils.py")))

    Meta.load_hanlp_recognizer()
    print("hanlp ZH model load success")

    # while True:
    #     update.update_db()
    #     time.sleep(Meta.SLEEP_UPDATE)

    update.create_fake_data()
    update.update_db()

    Meta.unload_hanlp_recognizer()