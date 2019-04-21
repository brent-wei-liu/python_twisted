
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
            if not self.done:
                reactor.callLater(1, self.count)

from twisted.internet import reactor
calls = [Countdown('C1', 5), Countdown('C2', 3)]
for call in calls:
    reactor.callWhenRunning(call.count)

def monitor():
    if all([call.done for call in calls]):
        reactor.stop()
    else:
        reactor.callLater(1, monitor)

reactor.callWhenRunning(monitor)

print 'Start!'
reactor.run()
print 'Stop!'
