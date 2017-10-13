'''
This module provides a 'connection' function which listens on a TCP/IP
socket for a connection.

This module was abstracted from the GDB transport module in order to
allow use by the Xilinx xvc driver; when I get a chance to test, I might
make GDB use this.

Call the connection function with a reference to a command processor.

TODO: Add ability to have multiple connections to different cores.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

import re
import select
import socket
import SocketServer
import collections

def logger(what):
    print what

def socketrw(socket, logger=None, readsize=2048):
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

    def write(data, packetize=None):
        if logger is not None:
            logdata = data
            if len(logdata) > 40:
                logdata = "%s..." % repr(logdata[:40])
            else:
                logdata = repr(logdata)
            logger("Sending %s%s\n" % (packetize and 'packet ' or '', logdata))
        if packetize is not None:
            data = packetize(data)
        while data:
            data = data[send(data):]

    return read, write

def connection(cmdprocess, procname, address, run=True, logpackets=True, logger=logger, readsize=2048):

    class RequestHandler(SocketServer.BaseRequestHandler):
        def setup(self):
            logger("Connected to %s:%s -- now serving %s" % (self.client_address + (procname,)))
            # Ask the network driver to send packets immediately
            self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        def finish(self):
            logger("Client disconnected.\n\nWaiting for %s connection on %s:%s  (Ctrl-C to exit)" %
                ((procname,) + self.server.server_address))

        def handle(self):
            read, write = socketrw(self.request, logpackets and logger or None, readsize)
            cmdprocess(read, write)

    server = SocketServer.TCPServer(('', address), RequestHandler)

    if run:
        logger("Waiting for %s connection on %s:%s  (Ctrl-C to exit)" %
                ((procname,) + server.server_address))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger("\nKeyboard Interrupt received; exiting...\n")
    return server
