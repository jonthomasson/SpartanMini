'''
This module provides a 'connection' function which listens on a TCP/IP
socket for a connection from GDB.

Call the connection function with a reference to a command processor,
such as an object that is an instance of a subclass of CmdGdb.

TODO: Add ability to have multiple connections to different cores.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

import re
import select
import socket
import SocketServer
import collections

splitter = re.compile(r"(^[^$#\03+-]*[\03+-]|\$[^#]*#..|#..)").split
calcsum = lambda x: sum((ord(x) for x in x), 0) % 256

def lowlevel(read, write, cmdprocess, poll_ms=20,
                     len=len, sum=sum, ord=ord, int=int, callable=callable,
                     splitter=splitter, calcsum=calcsum):

    class Ack:
        pass

    class Nak:
        pass

    def send(data, outbound = collections.deque()):
        if data is Ack:
            if outbound:
                outbound.popleft()
            sendit = outbound
        elif data is Nak:
            sendit = outbound
        else:
            sendit = not outbound
            outbound.append(data)
        if sendit:
            write(outbound[0], True)

    cmdprocess.async_send = send

    line = ''
    maxread = cmdprocess.maxread
    pollfunc = None
    polling = None
    while 1:
        # Read data, or None for a timeout (for polling)
        while 1:
            data = splitter(line, 1)
            if len(data) >= 3:
                break
            if pollfunc is None:
                data = read(None)
            else:
                data = read(poll_ms)
                if data is None:
                    polling = 1
                    break
            if not data:
                cmdprocess.disconnect()
                return
            line = (line + data)[-maxread:]

        if data is not None:
            # Check for out of band +, -, ctl-C
            packet, line = data[1:]
            if packet[-1] in '+-\3':
                if packet[-1] == '+':
                    send(Ack)
                    if line[:1] == '-':  # Some sort of goofy GDB bug seen on mon command sometimes
                        line = line[1:]
                    continue
                elif packet[-1] == '\3':
                    polling = 2
                else:
                    send(Nak)
                    continue
            else:
                # Process the packet and get the result
                assert packet[-3] == '#'   # Check compiled RE for accuracy...
                data = packet[1:-3]
                try:
                    checksum = int(packet[-2:], 16)
                except TypeError:
                    ok = False
                else:
                    ok = packet[0] == '$' and data
                    ok = ok and calcsum(data) == checksum
                write('-+'[ok], False)
                if not ok:
                    continue
                # Stop polling (if we were) and process the packet
                pollfunc = pollfunc and pollfunc(2) and None
                data = cmdprocess(data)

        # Poll the command processor if necessary
        if polling is not None:
            if pollfunc is None:
                print "Ctrl-C received when not polling..."
                polling = None
                continue
            data = pollfunc(polling-1)
            polling = None
            if data is None:
                continue
            pollfunc = None

        # Take returned data, and make it a poll func, or send it on
        if callable(data):
            pollfunc = data
        else:
            send(data)

def logger(what):
    print what

def socketrw(socket, logger=None, calcsum=calcsum, readsize=2048):
    recv, send = socket.recv, socket.send
    try:
        POLLIN = select.POLLIN
    except AttributeError:
            def poll(timeout):
                return select.select([socket], [], [], timeout/1000.0)[0]
    else:
        poll = select.poll()
        poll.register(socket, POLLIN)
        poll = poll.poll

    def read(timeout=None):
        if timeout is not None and not poll(timeout):
            return None
        data=recv(readsize)
        if logger is not None:
            logdata = data
            if len(logdata) > 40:
                logdata = "%s..." % repr(logdata[:40])
            else:
                logdata = repr(logdata)
            logger("Received %s" % logdata)
        return data

    def write(data, packetize):
        if logger is not None:
            logdata = data
            if len(logdata) > 40:
                logdata = "%s..." % repr(logdata[:40])
            else:
                logdata = repr(logdata)
            logger("Sending %s%s" % (packetize and 'packet ' or '', logdata))
        if packetize:
            data = '$%s#%02x' % (data, calcsum(data))
        while data:
            data = data[send(data):]

    return read, write

def connection(cmdprocess, address=2222, run=True, logpackets=True, logger=logger):

    class RequestHandler(SocketServer.BaseRequestHandler):
        def setup(self):
            logger("Connected to %s:%s -- now serving GDB" % self.client_address)
            # Ask the network driver to send packets immediately
            self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        def finish(self):
            logger("Client GDB disconnected.\n\nWaiting for connection on %s:%s  (Ctrl-C to exit)" % self.server.server_address)

        def handle(self):
            read, write = socketrw(self.request, logpackets and logger or None)
            lowlevel(read, write, cmdprocess)

    server = SocketServer.TCPServer(('', address), RequestHandler)

    if run:
        logger("Waiting for connection on %s:%s  (Ctrl-C to exit)" % server.server_address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger("\nKeyboard Interrupt received; exiting...\n")
    return server
