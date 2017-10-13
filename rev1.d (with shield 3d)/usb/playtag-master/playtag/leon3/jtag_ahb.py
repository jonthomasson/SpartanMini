#! /usr/bin/env python
'''
This module provides a LeonMem class that can read and write memory on a LEON processor
through JTAG.  It directly relies on the jtagcommands module, and when you instantiate
a LeonMem instance, you must pass it a cable driver that it can use for physical communication.

Currently it is pretty stupid.  Assumes a single LEON is the only thing in the JTAG chain.

Future refactoring should include:

  - Allowing other devices in the JTAG chain.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

from ..bsdl.lookup import readfile, PartParameters, PartInfo
from ..jtag.discover import Chain
from ..jtag.template import JtagTemplate, TDIVariable
from ..lib.bus32 import Bus32

class LeonPart(PartParameters):
    ''' Reads part from standard Gaisler Research config file.
    '''
    # DevName DevID DevIDMask IRlength hasdebug cmdi datai

    def __init__(self, line):
        linetext = ' '.join(line)
        try:
            name = line.pop(0)
            params = [int(x, 0) for x in line]
            idcode, mask, irlen, hasdebug = params[:4]
            if hasdebug:
                self.is_leon = True
                self.cmdi, self.datai = params[4:]
            idcode = idcode, mask
            ir_capture = 'x' * (irlen - 2) + '01'
            self.base_init(idcode, ir_capture, name)
        except:
            print "\nError processing line: %s\n" + linetext
            raise


class BusDriver(dict):
    big_endian = True
    addr_align = 1024
    max_bytes = 16384

    data_var = TDIVariable(1)

    def __init__(self, jtagrw, UserConfig):
        PartInfo.addparts(LeonPart(x) for x in readfile(UserConfig.JTAGID_FILE))
        chain = Chain(jtagrw)
        leons = [x for x in chain if hasattr(x.parameters, 'is_leon')]
        err = len(leons) != 1
        if err or UserConfig.SHOW_CHAIN:
            print str(chain)
            if not leons:
                raise SystemExit("Did not find LEON3 processor in chain")
            if not chain:
                raise SystemExit("Did not find devices in JTAG chain")
            if len(leons) > 1:
                raise SystemExit("Multi-LEON3 chains not yet supported")

        leon = leons[0]
        self.ilength = len(leon.ir_capture)
        self.cmdi = leon.parameters.cmdi
        self.datai = leon.parameters.datai
        self.bypass_info = leon.bypass_info
        if not self.ilength or not self.cmdi or not self.datai:
            raise SystemExit("Invalid LEON parameters")
        self.jtagrw = jtagrw

    def __missing__(self, key):
        ''' Create a JTAG command template to read or write
            a byte, a halfword, or any power-of-2 number of
            words.
        '''
        write, length, size = key
        name = '%s_%d_%d' % ('write' if write else 'read', length, size)
        data = self.data_var if write else 0
        self[key] = cmd = JtagTemplate(self.jtagrw, name, bypass_info=self.bypass_info)
        outerloop = (length + 255) / 256
        innerloop = (length + 255) % 256
        if outerloop:
            assert (outerloop == 1) or (innerloop == 255), length
            assert (length == 1) or (size == 4), (length, size)

            ilength, cmdi, datai = self.ilength, self.cmdi, self.datai
            businfo = {1:0, 2:1, 4:2}[size] + write * 4
            readwrite = cmd.writed if write else cmd.readd
            cmd.update(cmd.select_dr).loop()
            cmd.writei(ilength, cmdi).writed(32, adv=0).writed(3, businfo)
            cmd.writei(ilength, datai).loop()
            readwrite(32, tdi=data, adv=0).writed(1, 1).endloop(innerloop)
            readwrite(32, tdi=data, adv=0).writed(1, 0).endloop(outerloop)
        return cmd

    def readsingle(self, addr, size):
        ''' Read an aligned byte, halfword, or word
        '''
        cmd = self[False, 1, size]
        yield (cmd([addr]).next() << (8 * (size + (addr & 3)))) >> 32

    def writesingle(self, addr, size, value):
        ''' Write an aligned byte, halfword, or word
        '''
        cmd = self[True, 1, size]
        cmd([addr], [value << (8 * (4 - size - (addr & 3)))])


    def readmultiple(self, addr, length):
        ''' Read a power of 2 number of words.
            AHB transfers should not cross 1024-byte blocks, so
            we send one read address for each block.
        '''
        cmd = self[False, length, 4]
        addr = range(addr, addr + length * 4, 1024)
        for word in cmd(addr):
            yield word

    def writemultiple(self, addr, value, offset, length):
        ''' write a power of 2 number of words.
            AHB transfers should not cross 1024-byte blocks, so
            we send one write address for each block.
        '''
        cmd = self[True, length, 4]
        addr = range(addr, addr + length * 4, 1024)
        cmd(addr, value[offset:offset+length])

def LeonMem(jtagrw, UserConfig):
    return Bus32(BusDriver(jtagrw, UserConfig))
