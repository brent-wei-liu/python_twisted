
class Countdown(object):

    def __init__(self, name, counter):
        self.name = name
        self.counter = counter
        self.done = False

    def count(self):
        if self.counter == 0:
            self.done = True
        else:
            print self.name, self.counter, '...'
            self.counter -= 1

from twisted.internet import reactor
from twisted.internet import task

calls = [Countdown('C1', 5), Countdown('C2', 3)]
for call in calls:
    t = task.LoopingCall(call.count)
    t.start(1.0)

def monitor():
    if all([call.done for call in calls]):
        reactor.stop()

call1 = task.LoopingCall(monitor)
call1.start(1.0)

print 'Start!'
reactor.run()
print 'Stop!'
