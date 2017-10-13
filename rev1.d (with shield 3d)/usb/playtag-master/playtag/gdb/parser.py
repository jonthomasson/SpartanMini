'''
This module supplies the CmdGdb class.

This class is designed to be called with GDB remote debugging protocol packets,
and return reply packets.

In general, this class provides the parsing and return formatting.
Subclass it to provide processor-dependent functions.

This module has no direct dependencies, although it relies on its subclass
providing certain functions.

NOTE:

During development of this module, I experimented with implementing
the X (binary memory write) and p/P (single register read/write) packets,
but these were actually slower once I configured GDB properly.

Proper configuration includes:

set download-write-size 16384
set remote memory-write-packet-size 8211
set remote memory-write-packet-size fixed
set remote memory-write-packet-size 8196

The "8211" and "8196" for the packet sizes have been carefully
crafted so that the full packet includes an even number of kilobytes
of payload.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

import re
import traceback

def emptystr(*x):
    return ''

fmthex = dict((x,'%%0%dx' % x) for x in (1 << x for x in range(5)))

def int2hex(intlist, width, fmthex=fmthex, len=len):
    fmt = fmthex[width]
    result = ''.join(fmt % x for x in intlist)
    if len(result) != len(intlist) * width:
        raise ValueError("Integer too big in conversion from int to string")
    return result

def chr2hex(chrstr, ord=ord, int2hex=int2hex):
    return int2hex([ord(x) for x in chrstr], 2)

def hex2int(hexstr, width, int=int, xrange=xrange, len=len):
    return [int(hexstr[i:i+width], 16) for i in xrange(0, len(hexstr), width)]

def hex2chr(hexstr, chr=chr, hex2int=hex2int):
    return ''.join(chr(x) for x in hex2int(hexstr, 2))

def splitstuff(s, hasdata=False, splitch=',', int=int):
        addr, length = s.split(splitch, 1)
        if hasdata:
            splitch = isinstance(hasdata, str) and hasdata or ':'
            length, data = length.split(splitch, 1)
        addr, length = int(addr, 16), int(length, 16)
        return hasdata and (addr, length, data) or (addr, length)

class CmdGdb(object):

    maxread = 17000

    stopcode = 0x05

    def __call__(self, data, emptystr=emptystr):
        try:
            result = getattr(self, 'cmd_' + data[0], emptystr)(data[1:])
            if result is None:
                raise ValueError('Invalid cmd: %s' % data)
        except Exception:
            traceback.print_exc()
            result = 'E99'
        return result

    def cmd_g(self, data, int2hex=int2hex):
        ''' Read registers
        '''
        return int2hex(*self.readregs())

    def cmd_G(self, data, hex2int=hex2int):
        ''' Write registers
        '''
        numregs = self.NUMREGS
        regchars = self.REGSIZE * 2
        if len(data) != numregs * regchars:
            raise ValueError
        self.writeregs(hex2int(data, regchars))
        return 'OK'

    if 0:
        # NOTE:  These work, but are dog-slow on the LEON core
        def cmd_p(self, data, int=int):
            ''' Read one register
            '''
            return '%08x' % self.readreg(int(data,16))

        def cmd_P(self, data, splitstuff=splitstuff):
            ''' Write one register
            '''
            self.writereg(*splitstuff(data, splitch='='))
            return 'OK'

    def cmd_m(self, data, splitstuff=splitstuff):
        '''  Read memory.  Let the low-level memreader
             decide whether to read bytes, words, half-words, whatever
        '''
        return self.readmemstring(*splitstuff(data))

    def cmd_M(self, data, splitstuff=splitstuff):
        '''  Write memory.  Call the low-level memwriter
             to get the function to write with and the number
             of hex chars per item.
        '''
        addr, length, data = splitstuff(data, True)
        if len(data) != length * 2:
            raise ValueError("Length of data string does not match command length")
        self.writememstring(addr, data)
        return 'OK'

    if 0:
        # NOTE: This might be an option for a slow link, but is actually
        #       slower in the lab.
        def cmd_X(self, data, splitstuff=splitstuff, ord=ord):
            '''  Write memory in binary format
            '''
            addr, length, data = splitstuff(data, True)
            data2 = [[ord(x) for x in y] for y in data.split('}')]
            for index in range(1, len(data2)):
                data2[index][0] ^= 0x20
            data = []
            for item in data2:
                data += item
            if len(data) != length:
                raise ValueError("Length of data string does not match command length")
            if data:
                self.writemembytes(addr, data)
            return 'OK'

    def cmd_Z(self, data, insert=True, splitstuff=splitstuff):
        btype, addr, size = splitstuff(data, ',')
        result = self.set_breakpoint(insert, btype, addr, int(size, 16))
        if result is None:
            return ''
        if result == 0:
            return 'OK'
        return 'E%02x' % result

    def cmd_z(self, data):
        return self.cmd_Z(data, False)

    def cmd_q(self, data, splitter=re.compile(r'(\w+)').split, emptystr=emptystr):
        discard, query, data = splitter(data,1)
        if discard:
            raise ValueError("Invalid q command received")
        return getattr(self, 'query_' + query, emptystr)(data[1:])

    def query_Supported(self, data):
        return 'PacketSize=%h' % (self.maxread/2 - 10)

    def query_Rcmd(self, data, chr2hex=chr2hex, hex2chr=hex2chr):
        return chr2hex(self.monitor(hex2chr(data)))

    def write_console(self, line):
        if hasattr(self, 'async_send'):
            self.async_send('O' + chr2hex(line))
        else:
            print line

    def break_status(self, *data):
        '''  Return the reason why we stopped
        '''
        return 'S%02x' % self.stopcode
    vars()['cmd_?'] = break_status

    def cmd_c(self, data):
        ''' Continue at optional address
        '''
        if data.strip():
            return 'E02'

        checkstop = self.cpu_pollstop()
        def poll(ctrlc=False):
            if checkstop(ctrlc):
                return self.break_status()
            return poll
        return poll()

    def monitor(self, cmd):
        cmd = cmd.split()
        proc = getattr(self, 'monitor_' + cmd[0], None)
        if proc is None:
            return "\nMonitor command '%s' not supported\n\n" % cmd[0]
        result = proc(' '.join(cmd[1:]))
        if result:
            result = '\n%s\n\n' % result
        else:
            result = '\n'
        return result

    def disconnect(self):
        pass
