#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, threading, abc
from optparse import OptionParser
import Queue
import logging
import traceback

class POISON_PILL:
    pass

def parse_options():
    parser = OptionParser()
    parser.add_option("-t", action="store", type="int",
                      dest="workerNum", default=2,
                      help="worker number [1]")
    (options, args) = parser.parse_args()
    return options

class Producer(threading.Thread):
    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.kill_flag = False

    def run(self):
        i = 0
        while not self.kill_flag:
            try:
                logging.info("%s is active", self.name)
                self.q.put(i, timeout=1)
                i += 1
                time.sleep(0.5)
            except Queue.Full as e:
                logging.info("[%s] queue is full.", self.name)

        logging.info('Stop thread %s', self.name)

class Worker(threading.Thread):
    def __init__(self, name, q, downStreamQ):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.kill_flag = False
        self.downStreamQ = downStreamQ

    def run(self):
        while not self.kill_flag:
            try:
                logging.info("%s is active", self.name)
                product = self.q.get(1, timeout=1)
                if product == POISON_PILL: break
                logging.info("Consuming: " + str(product))
                self.downStreamQ.put(product, timeout=1)
                #self.q.task_done() tell q.join() something is done
            except Queue.Empty as e:
                logging.info("[%s] queue is empty.", self.name)
            except Queue.Full as e:
                logging.info("[%s] queue is full.", self.name)

        logging.info('Stop thread %s', self.name)

class Serializer(threading.Thread):
    def __init__(self, name, q, filename):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.kill_flag = False
        self.filename = filename
        self.file = open(filename, 'w')

    def run(self):
        while not self.kill_flag:
            try:
                logging.info("%s is active", self.name)
                product = self.q.get(timeout=1)
                logging.info("Writing : " + str(product))
                self.file.write('%d\n'%product)
                self.q.task_done()
            except Queue.Empty as e:
                logging.info("[%s] queue is empty.", self.name)
        logging.info('Stop thread %s', self.name)
        self.file.flush()
        self.file.close()


def has_live_threads(threads):
    return True in [t.isAlive() for t in threads]

def main():
    options = parse_options()
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    work_queue = Queue.LifoQueue()
    output_queue = Queue.LifoQueue()

    threads = []
    #q = None
    try:
        threads.append(Producer("[receiver 0]", work_queue))
        threads.append(Serializer("[serializer 0]",
                                  output_queue,'output.txt'))

        for i in range(options.workerNum):
            threads.append(Worker("[worker %s]" % str(i),
                                  work_queue, output_queue))

        for t in threads: t.start()
    except IOError as e:
        #logging.fatal("I/O error(%d): %s", e.errno, e.strerror, exc_info=True)
        logging.fatal("I/O error(%d): %s : %s", e.errno, e.strerror, e.filename)
        sys.exit(-1)

    while has_live_threads(threads):
        try:
            # synchronization timeout of threads kill
            [t.join(1) for t in threads if t is not None and t.isAlive()]
        except KeyboardInterrupt:
            # Ctrl-C handling and send kill to threads
            logging.info('Sending kill to threads...')
            for t in threads:
                logging.info('Sending kill to thread %s', t.name)
                t.kill_flag = True
                work_queue.put(POISON_PILL)
    output_queue.join() # wait until all of the products are done
    print "Exited"


if __name__ == '__main__':
    main()