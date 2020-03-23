
import update
import time
import Meta

if __name__ == '__main__':
    Meta.load_hanlp_recognizer()
    print("start db operations")
    update.update_db()
    Meta.unload_hanlp_recognizer()

    '''
    while True:
        update.update_db()
        time.sleep(Meta.SLEEP)
    '''