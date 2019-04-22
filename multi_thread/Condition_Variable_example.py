'''
https://web.stanford.edu/~ouster/cgi-bin/cs140-spring14/lecture.php?topic=locks

Condition Variables
Synchronization mechanisms need more than just mutual exclusion;
also need a way to wait for another thread to do something
(e.g., wait for a character to be added to the buffer)

Condition variables: used to wait for a particular condition to
become true (e.g. characters in buffer).

1. wait(condition, lock): release lock, put thread to sleep
   until condition is signaled; when thread wakes up again,
   re-acquire lock before returning.

2. signal(condition, lock): if any threads are waiting on
   condition, wake up one of them. Caller must hold lock, which
   must be the same as the lock used in the wait call.

3. broadcast(condition, lock): same as signal, except wake up
all waiting threads.
Note: after signal, signaling thread keeps lock, waking thread
goes on the queue waiting for the lock.
Warning: when a thread wakes up after cond_wait there is no
guarantee that the desired condition still exists: another
thread might have snuck in.
'''

'''
Producer/Consumer, version 3 (with condition variables):
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
        with cv:
            q.appendleft(i)
            cv.notify()
        i += 1
        time.sleep(1)

    with cv:
        q.appendleft(POISON_PILL)
        cv.notify()

    print '%s done ...\n' % threading.currentThread().name


def get():
    while True:
        with cv:
            while not q:
                cv.wait()
            x = q.pop()
            if x == POISON_PILL: break
            print 'Consuming: ', x
    print 'get done ...\n'

q = deque()
cv = threading.Condition()
threading.Thread(target=put, name='Producer').start()
threading.Thread(target=get, name='Consumer').start()