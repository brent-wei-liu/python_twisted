# This is the blocking Get Poetry Now! client.
import datetime, optparse, socket

def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...
This is the Get Poetry Now! client, blocking edition.
Run it like this:
  python blocking-client/get-poetry.py 10001 10002 10003
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

def main():
    addresses = parse_args()
    elapsed = datetime.timedelta()
    for i, address in enumerate(addresses):
        host, port = address
        addr_fmt = '%s:%s' % (host or '127.0.0.1', port)
        print 'Task %d: get poetry from: %s' % (i + 1, addr_fmt)
        start = datetime.datetime.now()
        # Each execution of 'get_poetry' corresponds to the
        # execution of one synchronous task in Figure 1 here:
        # http://krondo.com/?p=1209#figure1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        poem = ''
        while True:
            data = sock.recv(1024)  # block here
            if not data:
                sock.close()
                break
            poem += data
            print data
        time = datetime.datetime.now() - start
        msg = 'Task %d: got %d bytes of poetry from %s in %s'
        print  msg % (i + 1, len(poem), addr_fmt, time)
        elapsed += time
    print 'Got %d poems in %s' % (len(addresses), elapsed)

if __name__ == '__main__':
    main()
