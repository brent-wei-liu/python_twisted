import threading
import time

class Thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global count
        caller = self.getName()
        while True:
            with lock:
                if count >= 5: break
                print "%s: Acquired the lock: %d" % (caller, count)
                count += 1
            time.sleep(1)

count = 0
lock = threading.Lock()

Thread('Thread-1').start()
Thread('Thread-2').start()

