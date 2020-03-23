
import update
import time
import Meta

if __name__ == '__main__':
    Meta.load_hanlp_recognizer()
    update.create_fake_data()
    Meta.unload_hanlp_recognizer()

    '''
    while True:
        update.update_db()
        time.sleep(Meta.SLEEP)
    '''