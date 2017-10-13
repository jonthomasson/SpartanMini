'''
This module subclasses CmdGdb to provide a GDB command processor for the Leon core.

It assumes a lower-level transport, such as that provided by leonmem.  When you
construct the CmdProcessor object, pass it the low-level transport object as the
ahb.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

from itertools import izip
from ..gdb.parser import CmdGdb, hex2int, int2hex
from .cpustate import LeonCfg
from .traptypes import traptypes

class CmdProcessor(CmdGdb):
    NUMREGS = 72
    REGSIZE = 4

    PSR_INIT = 0x00c0

    def writememstring(self, addr, data):
        ''' Write a string to an address.
        '''
        return self.ahb_writestring(self.remap_addr(addr), data)

    def writemembytes(self, addr, data):
        ''' Write binary bytes to address
        '''
        addr = self.remap_addr(addr)
        return self.ahb_writebyte(addr, data)

    def readmemstring(self, addr, length):
        return self.ahb_readstring(self.remap_addr(addr), length)

    def reglocs(self):
        # TODO: MAP REGISTERS TO STACK MEMORY
        '''  The LEON registers are available in the DSU, but due
             to implementation details relating to the windowed nature
             of the SPARC, the memory address for a particular register
             can change based on the value of the current window pointer
             in the program status register.
             This function returns the base addresses of each group of
             registers in memory.
        '''
        leoncfg = self.leoncfg
        base = leoncfg.dsu.IUREG.baseaddr
        mod = leoncfg.NUM_WINDOWS * 64
        g = base + mod
        s = leoncfg.dsu.SPECIALREG.baseaddr
        psr = self.psr
        while 1:
            cwp = psr.load().CWP
            o = base + (((cwp * 64) + 32) % mod)
            l = base + (((cwp * 64) + 64) % mod)
            i = base + (((cwp * 64) + 96) % mod)
            yield g, o, l, i, s

    def regaddrs(self, extension=32*[None]):
        result = [x+y for x in self.reglocs() for y in range(0,32,4)]
        result[32:32] = extension
        return result

    def readregs(self, fpregs=32*[0]):
        result = []
        for addr in self.reglocs():
            result.extend(self.ahb_read(addr, 8))
        result[32:32] = fpregs
        return result, 8

    def writeregs(self, value):
        value = value[0:8], value[8:16], value[16:24], value[24:32], value[64:72]
        for (addr, value) in zip(self.reglocs(), value):
            self.ahb_write(addr, value)

    def readreg(self, index):
        addr = self.regaddrs()[index]
        if addr is None:
            return 0
        return self.ahb_read(addr)

    def writereg(self, index, data):
        addr = self.regaddrs()[index]
        if addr is not None:
            self.ahb_write(self.regaddrs()[index], data)

    def cpu_pollstop(self):

        def poll(ctrlc=False):
            ctl = load_dsuctl()
            brk = load_dsubrk()
            if not ctl.value & stopmask:
                if not ctrlc:
                    return
                if not ctl.EE:
                    self.write_console('\nWarning: DSU disabled!  System in inconsistent state.\n')
                store_dsubrk(1)

            store_dsuctl()
            trap = load_dsutrap()
            status = [traptypes[trap.TYPE] + (trap.EM and ' (error)' or '')]
            if ctl.PW:
                status.append('powered-down')
            if ctl.HL:
                status.append('halted')
            if ctl.PE:
                status.append('proc error')
            if brk.BN0:
                status.append('DSU break')
            self.write_console('\nCPU Info: %s\n' % ', '.join(status))
            self.flushcache()
            self.ahb_write(0)
            return True

        load_dsuctl = self.load_dsuctl
        load_dsubrk = self.load_dsubrk
        load_dsutrap = self.load_dsutrap
        store_dsuctl = self.store_dsuctl
        store_dsubrk = self.store_dsubrk
        stopmask = self.stopmask
        store_dsuctl()
        store_dsubrk(0)
        return poll

    def set_breakpoint(self, insert, btype, addr, size):
        if not btype:
            return         # SW breakpoints not directly supported
        if btype> 4:
            return 21      # Error -- unknown breakpoint
        watcharray = self.watcharray
        end = addr + size + 3
        end = max(end - (end & 3), 4)
        addr -= addr & 3
        size = end - addr
        if size & (size-1):
            return 20      # Error -- must be binary
        ex = btype in (1,4)
        wr = btype in (2,4)
        rd = btype in (3,4)
        mask = (1 << 32) - size
        bytes = addr + ex, mask + rd * 2 + wr
        if insert != (bytes in watcharray):
            if insert:
                if None not in watcharray:
                    return 29    # No watchpoints available
                wpnum = watcharray.index(None)
                watcharray[wpnum] = bytes
            else:
                wpnum = watcharray.index(bytes)
                watcharray[wpnum] = None
                bytes = addr, mask
            index = wpnum*2
            self.watchio[index:index+2] = bytes
        self.ahb_write(0)
        return 0

    def __init__(self, ahb, userconfig):
        self.leoncfg = leoncfg = LeonCfg(ahb, userconfig)
        self.reglocs = self.reglocs().next

        self.dsu = dsu = leoncfg.dsu
        self.ahb_read = ahb.read
        self.ahb_write = ahb.write
        self.ahb_readbyte = ahb.readbyte
        self.ahb_writebyte = ahb.writebyte
        self.ahb_writestring = ahb.writestring
        self.ahb_readstring = ahb.readstring
        self.psr = psr = dsu.PSR
        self.load_dsuctl = dsu.Control.load
        self.load_dsubrk = dsu.Break.load
        self.load_dsutrap = dsu.Trap.load
        self.store_dsubrk = dsu.Break.store
        dsuctl = dsu.Control
        dsuctl.PW = dsuctl.HL = dsuctl.PE = dsuctl.DM = 1
        self.stopmask = dsuctl.value
        self.store_dsuctl = dsuctl.store
        self.store_dsubrk(1)
        self.store_dsuctl(0x0C)
        self.store_dsuctl(0x20C)
        self.watchio = dsu.WatchPoints
        self.watcharray = leoncfg.NUM_WATCHPOINTS * [None]

        psr.store(self.PSR_INIT)
        reg = self.regaddrs()
        ahb.write(reg[14], leoncfg.STACKLOC)
        ahb.write(reg[30], leoncfg.STACKLOC)
        self.remap_addr = leoncfg.remap_addr
        self.flushcache = leoncfg.flushcache

    @staticmethod
    def parserange(line):
        result = (int(x, 0) for x in line.replace(':').split())
        if len(line) == 1:
            line = line[0], line[0] + 4
        return line

    def monitor_clear(self, line):
        leoncfg = self.leoncfg
        if not line.strip():
            addr, end = leoncfg.AHB_RAM_ADDR, leoncfg.AHB_RAM_ADDR + leoncfg.AHB_RAM_SIZE
        else:
            addr, end = self.parserange(line)
        length = end - addr
        if (addr | length) & 3:
            self.ahb_writebyte(addr, length * [0])
        else:
            self.ahb_write(addr, length / 4 * [0])
        self.ahb_write(0)
        return "Cleared 0x%08x bytes at 0x%08x" % (length, addr)

    def monitor_verify(self, line):
        line = line.strip()
        try:
            f = open(line, 'rb')
            data = f.read().split()
            f.close()
        except:
            return "Could not read file %s" % repr(line)
        try:
            data = [int(x,16) for x in data]
        except:
            return "Invalid data in file %s" % line
        self.write_console('\nVerifying...')
        verif = self.ahb_read(self.leoncfg.AHB_RAM_ADDR, len(data))
        if verif == data:
            return "0x%08x bytes verified OK" % (len(data) * 4)
        bad = []
        for index, (expected, actual) in enumerate(zip(data, verif)):
            if expected != actual:
                bad.append((index, expected, actual))
        if not bad:
            return "Unknown verification error"

        self.write_console('\n\n%d errors\n\n' % len(bad))
        if len(bad) > 40:
            self.write_console('    (Displaying first 40)\n\n')
        self.write_console('Address     Expected    Actual\n')
        for stuff in bad[:40]:
            self.write_console('0x%08x  0x%08x  0x%08x\n' % stuff)

    def monitor_load(self, line):
        try:
            f = open(line, 'rb')
            data = f.read().split()
            f.close()
        except:
            return "Could not read file %s" % line
        try:
            data = [int(x,16) for x in data]
        except:
            return "Invalid data in file %s" % line
        self.write_console("\n\nWriting 0x%08x bytes at 0x%08x..." % (len(data) * 4, self.leoncfg.AHB_RAM_ADDR))
        self.ahb_write(self.leoncfg.AHB_RAM_ADDR, data)
        self.ahb_write(0)
        return "Done."

    def monitor_reset(self, line):
        if '-q' not in line.split():
            self.write_console("\n\nResetting the CPU.\n\nNOTE:  GDB DOESN'T KNOW THIS AND REGISTERS WILL BE WRONG!!!")
        self.leoncfg.reset()
        self.ahb_write(0)
        self.watcharray = self.leoncfg.NUM_WATCHPOINTS * [None]
