
'''
Producer/Consumer, version 4 (with Semaphore):
'''
from collections import deque
import threading
import time

class POISON_PILL:
    pass

i = 0
def put():
    global i
    while i < 5:
        P(empty_count)
        q.appendleft(i)
        i += 1
        V(fill_count)
        time.sleep(1)

    P(empty_count)
    q.appendleft(POISON_PILL)
    V(fill_count)

    print '%s done ...\n' % threading.currentThread().name


def get():
    while True:
        P(fill_count)
        x = q.pop()
        if x == POISON_PILL: break
        print 'Consuming: ', x
        V(empty_count)
    print 'get done ...\n'


def P(sem):
    sem.acquire()
def V(sem):
    sem.release()

# Buffer size
N = 10
q = deque()
fill_count = threading.Semaphore(0)
empty_count = threading.Semaphore(N)

threading.Thread(target=put, name='Producer').start()
threading.Thread(target=get, name='Consumer').start()