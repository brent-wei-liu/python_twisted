# This is the Twisted Get Poetry Now! client, version 2.1.

# NOTE: This should not be used as the basis for production code.

import optparse

from twisted.internet.protocol import Protocol, ClientFactory


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...
This is the Get Poetry Now! client, Twisted version 2.1.
Run it like this:
  python twisted-client-2/get-poetry-simple.py 10001 10002 10003
"""
    parser = optparse.OptionParser(usage)
    _, addresses = parser.parse_args()
    if not addresses:
        print parser.format_help()
        parser.exit()
    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)
        if not port.isdigit():
            parser.error('Ports must be integers.')
        return host, int(port)
    return map(parse_address, addresses)

class PoetryProtocol(Protocol):
    poem = ''
    def dataReceived(self, data):
        self.poem += data

    def connectionLost(self, reason):
        self.factory.poem_finished(self.poem)

class PoetryClientFactory(ClientFactory):

    protocol = PoetryProtocol # tell base class what proto to build

    def __init__(self, poetry_count):
        self.poetry_count = poetry_count
        self.poems = []

    def poem_finished(self, poem=None):
        if poem is not None:
            self.poems.append(poem)
        self.poetry_count -= 1

        if self.poetry_count == 0:
            self.report()
            from twisted.internet import reactor
            reactor.stop()

    def report(self):
        for poem in self.poems:
            print poem

    def clientConnectionFailed(self, connector, reason):
        print 'Failed to connect to:', connector.getDestination()
        self.poem_finished()


def poetry_main():
    addresses = parse_args()
    factory = PoetryClientFactory(len(addresses))
    from twisted.internet import reactor
    for address in addresses:
        host, port = address
        reactor.connectTCP(host, port, factory)
    reactor.run()

if __name__ == '__main__':
    poetry_main()
