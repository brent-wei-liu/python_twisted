# This is the asynchronous Get Poetry Now! client.
'''
The main differences between it and the synchronous client:
1. 一次connect所有服务端
2. 每个socket设置为非阻塞 setblocking(0).
3. 阻塞在select直到有某个socket ready to read
4. 读数据的时候我们一次性把一个socket里面的数据全部读出到缓存，直到其没有
数据即将阻塞，然后我们换下一个socket继续读，如果没有socket ready，
阻塞到select。
这就意味着我们得记录每个socket的数据
'''
import datetime, errno, optparse, select, socket
import collections

def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...
This is the Get Poetry Now! client, asynchronous edition.
Run it like this:
  python async-client/get-poetry.py 10001 10002 10003
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

def polling_all_sockets(sockets):
    """Download poety from all the given sockets."""
    poems = collections.defaultdict(str) # socket -> accumulated poem
    # socket -> task numbers
    sock2task = {s: i+1 for i, s in enumerate(sockets)}
    sockets = list(sockets)  # make a copy
    # we go around this loop until we've gotten all the poetry
    # from all the sockets. This is the 'reactor loop'.
    while sockets:
        # this select call blocks until one or more of the
        # sockets is ready for read I/O
        rlist, _, _ = select.select(sockets, [], [])
        # rlist is the list of sockets with data ready to read
        for sock in rlist:
            data = ''
            while True:
                try:
                    new_data = sock.recv(1024)
                    if not new_data:
                        break
                    else:
                        data += new_data
                        # this break means:
                        # read 1024 bytes once a time
                        # break
                except socket.error:
                    # sock.recv will block,
                    # we continue the next available socket
                    break
            # Each execution of this inner loop corresponds to
            # working on one asynchronous task in Figure 3 here:
            # http://krondo.com/?p=1209#figure3
            task_num = sock2task[sock]
            if not data:
                sockets.remove(sock)
                sock.close()
                print 'Task %d finished' % task_num
            else:
                host, port =  sock.getpeername()
                msg = 'Task %d: got %d bytes from %s:%d'
                print msg % (task_num, len(data), host, port)
            poems[sock] += data
    return poems

def connect(address):
    """Connect to the given server and return a non-blocking socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Connect to %s:%d" % address
    sock.connect(address)
    sock.setblocking(0)
    return sock

def main():
    addresses = parse_args()
    start = datetime.datetime.now()
    sockets = [connect(address) for address in addresses]
    poems = polling_all_sockets(sockets)
    elapsed = datetime.datetime.now() - start
    for i, sock in enumerate(sockets):
        print 'Task %d: %d bytes of poetry' % (i + 1, len(poems[sock]))
    print 'Got %d poems in %s' % (len(addresses), elapsed)

if __name__ == '__main__':
    main()
