#! /usr/bin/env python

'''
This module contains basic action handlers for SVF commands.

Does not work with long TDO commands.
Assumes SMASK is always set.

Ignores frequency commands.

Sets to unknown state for TRSTN command.

Assumes system clock runs at 15x jtag clock.

Copyright (C) 2013 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

dotest = __name__ == '__main__'
if dotest:
    import sys
    sys.path.insert(0, '../..')

from playtag.svf.parser import ParseSVF
from playtag.jtag.template import JtagTemplate

class DummyDriver(object):
    def make_template(self, template):
        self.template = template
    def apply_template(self, *tdi):
        print 'Applying states', self.template.states, self.template.tms[:200]

class SvfActions(object):
    shiftstates = JtagTemplate.shift_ir, JtagTemplate.shift_dr
    curstate = JtagTemplate.unknown
    freqmult = 15   # Assumes that TCK frequency is this much faster than internal clock
    realdriver = True

    def __init__(self, fname, driver=None):
        if driver is None:
            driver = DummyDriver()
            self.realdriver = False
        self.driver = driver
        self.statecache = {}
        for data in ParseSVF().parse(fname):
            getattr(self, type(data).__name__)(data)

    def ignore(self, data):
        print "Ignoring", data
        print
    Frequency = ignore

    def TRST(self, data):
        self.curstate = JtagTemplate.unknown

    def State(self, data):
        prevstate = data.prevstate
        statelist = data.statelist
        assert prevstate == self.curstate
        self.curstate = statelist[-1]
        key = prevstate, statelist
        cache = self.statecache
        template = cache.get(key)
        if template is None:
            cache[key] = template = JtagTemplate(self.driver, startstate=prevstate)
            for state in statelist:
                template.update(state)
        template()

    def RunTest(self, data):
        prevstate = data.prevstate
        endstate = data.endstate
        runstate = data.runstate
        assert prevstate == self.curstate
        self.curstate = endstate
        assert data.secs == [None, None]
        numclocks = data.numclocks * (1 if data.use_sck else self.freqmult)
        key = numclocks, prevstate, runstate, endstate
        cache = self.statecache
        template = cache.get(key)
        if template is None:
            cache[key] = template = JtagTemplate(self.driver, startstate=prevstate)
            if runstate != prevstate:
                template.update(runstate)
            template.update(numclocks)
            if runstate != endstate:
                template.update(endstate)
        template()

    def Shift(self, data):
        #print "\n\nShifting\n\n"
        ok = data.header.length == 0 and data.trailer.length == 0
        assert ok, "Need to upgrade to allow multiples in chain"

        prevstate = data.prevstate
        endstate = data.endstate
        shiftstate = data.state
        assert prevstate == self.curstate
        self.curstate = endstate

        data = data.data
        length = data.length
        tdo, tdomask, tdi = data.TDO, data.MASK, data.TDI
        smallxfer = length <= 128
        if smallxfer:
            for info in (tdo, tdomask, tdi):
                info.data = ''.join(info.data),
        usetdo = data.TDO.length and [int(x, 16) for x in tdomask.data]
        usetdo = usetdo and max(usetdo) > 0
        cache = self.statecache
        if usetdo:
            if not smallxfer:
                assert 0, "long TDO not yet supported"
            tdomask = int(''.join(tdomask.data), 16)
            tdo     = int(''.join(tdo.data), 16)
            tdi     = int(''.join(tdi.data), 16)
            key     = prevstate, shiftstate, endstate, length, tdi
            template = cache.get(key)
            if template is None:
                assert shiftstate in self.shiftstates
                cache[key] = template = JtagTemplate(self.driver, startstate=prevstate)
                op = (template.readi, template.readd)[shiftstate == JtagTemplate.shift_dr]
                op(length, tdi=tdi)
                template.update(endstate)
            if self.realdriver:
                result = template().next()
                assert result & tdomask == tdo & tdomask, (result, tdo)
            else:
                template()
            return

        numchunks = len(tdi.data)
        assert numchunks
        if numchunks == 1:
            key = prevstate, shiftstate, endstate, length
            template = cache.get(key)
            if template is None:
                assert shiftstate in self.shiftstates
                cache[key] = template = JtagTemplate(self.driver, startstate=prevstate)
                op = (template.writei, template.writed)[shiftstate == JtagTemplate.shift_dr]
                op(length)
                template.update(endstate)
                #print template.states, template.tms, template.tdi, template.tdo
            template([int(tdi.data[0], 16)])
            return
        partial = [shiftstate] * (numchunks - 1)
        stuff = zip([prevstate] + partial, partial + [endstate], reversed(tdi.data))
        bitsleft = length
        for prevstate, endstate, data in stuff:
            length = min(len(data) * 4, bitsleft)
            bitsleft -= length
            key = prevstate, shiftstate, endstate, length
            template = cache.get(key)
            if template is None:
                assert shiftstate in self.shiftstates
                adv = endstate != shiftstate
                cache[key] = template = JtagTemplate(self.driver, startstate=prevstate)
                op = (template.writei, template.writed)[shiftstate == JtagTemplate.shift_dr]
                op(length, adv=adv)
                if adv:
                    template.update(endstate)
            template([int(data, 16)])

if dotest:
    from time import time
    starttime = time()
    fname, = sys.argv[1:]
    SvfActions(fname)
    print time() - starttime
