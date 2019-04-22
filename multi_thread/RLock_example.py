# -*- coding: utf-8 -*-
'''
Lock与RLock的区别
从原理上来说：在同一线程内，对RLock进行多次acquire()操作，程序不会阻塞。
每个thread都运行f()，f()获取锁后，运行g()，但g()中也需要获取同一个锁。如果用Lock，这里多次获取锁，就发生了死锁。
但我们代码中使用了RLock。在同一线程内，对RLock进行多次acquire()操作，程序不会堵塞，
'''
import threading
rlock = threading.RLock()

def f():
  with rlock:
    g()
    h()

def g():
  with rlock:
    h()
    do_something1()

def h():
  with rlock:
    do_something2()

def do_something1():
    print('do_something1')

def do_something2():
    print('do_something2')


# Create and run threads as follows
try:
    threading.Thread(target=f).start()
    threading.Thread(target=f).start()
    threading.Thread(target=f).start()
except Exception as e:
    print("Error: unable to start thread")
