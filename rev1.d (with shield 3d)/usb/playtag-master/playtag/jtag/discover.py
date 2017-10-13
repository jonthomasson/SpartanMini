'''

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

import collections
import itertools

from .template import JtagTemplate
from ..bsdl.lookup import PartInfo

binnum = '{0:b}'.format

class Chain(list):
    mindev_idcode = 2
    maxdev_idcode = 32
    maxdev_noid = 32
    max_irbits = 10     # Max instruction length
    min_irbits = 2      # At least INTEST, EXTEST, and BYPASS
    repeat_count = 4

    def error(self, msg):
        raise SystemExit('\nError: %s\n' % msg)

    def __init__(self, jtagrw, **kw):
        bad = set(kw) - set(vars(type(self)))
        if bad:
            self.error("Bad argument(s): %s" % ', '.join(sorted(bad)))
        vars(self).update(kw)
        self.jtagrw = jtagrw
        idcodes = self.repeat_read(self.read_ids, 'IDCODE')
        self.dev_ids = dev_ids = self.find_ids(idcodes)
        self.numdevs = len(dev_ids)
        ir = self.repeat_read(self.read_ir, 'IR')
        ilengths = self.find_ilengths(ir)
        if len(ilengths) > 1 and len(set(dev_ids)) != len(dev_ids):
            self.stripdups(ilengths)
        icapture = set(self.icapture_values(ir, x) for x in ilengths)
        self[:] = [PartInfo(x) for x in dev_ids]
        self.constrain_parts(icapture)
        if len(icapture) != 1:
            self.diagnose_chain(ir)
            raise SystemExit
        icapture, = icapture
        self.updateparts(icapture)
        self.reverse()
        self.add_bypass_info()

    def repeat_read(self, func, info):
        readset = set(func() for i in range(self.repeat_count))
        if len(readset) > 1:
            readset = sorted(readset)
            badlist = "\n    ".join(binnum(x) for x in readset)
            if info == 'IR':
                minval = maxval = readset[0]
                for x in readset:
                    minval &= x
                    maxval |= x
                if maxval < 2 * minval:
                    readset = [minval]
            if len(readset) > 1:
                self.error("Inconsistent JTAG reads (%s):\n    %s" % (
                    info, badlist))
        value, = readset
        return value

    def read_ids(self):
        while 1:
            maxlen = 32 * self.mindev_idcode + self.maxdev_noid + 1
            idinfo = JtagTemplate(self.jtagrw).readd(maxlen+33, tdi=1)().next()
            if self.checkread(idinfo, maxlen, "IDCODE/BYPASS"):
                break
            if self.mindev_idcode >= self.maxdev_idcode:
                self.error("JTAG chain appears to have more than %s devices in it." % self.maxdev_idcode)
            self.mindev_idcode = min(self.mindev_idcode * 2, self.maxdev_idcode)
        return idinfo

    def read_ir(self):
        max_irbits = self.max_irbits
        maxlen = self.numdevs * max_irbits + 1
        ir = JtagTemplate(self.jtagrw).readi(maxlen + max_irbits + 1, tdi=1)().next()
        if not self.checkread(ir, maxlen, "IR"):
            self.error("Unexpectedly long instruction register: %x" % binnum(ir))
        return ir

    def checkread(self, code, maxlen, op):
        mask = (1 << maxlen) - 1
        value = code & mask
        if not code:
            self.error("JTAG chain stuck at 0 (%s)" % op)
        if value == mask:
            self.error("JTAG chain stuck at 1 (%s)" % op)
        return not (code >> maxlen)

    def find_ids(self, idcodes):
        devices = []
        codelen = 32
        mask = (1 << codelen) - 1
        while idcodes & (idcodes-1):
            if not (idcodes & 1):
                devices.append(0)
                idcodes >>= 1
            else:
                devices.append(idcodes & mask)
                idcodes >>= codelen
            if not idcodes:
                self.error("Internal Error: idstring too short")
        if not devices:
            self.error("Empty JTAG chain -- data")
        return devices

    def find_ilengths(self, ir):
        numdevs = self.numdevs
        istring = binnum(ir)
        ones = [x for (x,y) in enumerate(reversed(istring)) if y == '1']
        total = ones.pop()
        if not ones:
            self.error("Empty JTAG chain -- instruction")
        if ones[0]:
            self.error("Illegal last device in chain: %s" % istring)
        if len(ones) < numdevs:
            self.error("Broken instruction register: expected %d devices, got:\n    %s" % (numdevs, istring))
        if numdevs == 1:
            return [(total,)]
        combinations = itertools.combinations(ones[1:], numdevs-1)
        start, end = (0,), (total,)
        combinations = [zip(x+end, start+x) for x in combinations]
        result = [tuple(x-y for (x,y) in z) for z in combinations]
        min_irbits = self.min_irbits
        return set(x for x in result if min(x) >= min_irbits)

    def stripdups(self, ilengths):
        devdict = collections.defaultdict(list)
        for i, x in enumerate(self.dev_ids):
            if x:
                devdict[x].append(i)
        dups = [x for x in devdict.itervalues() if len(x) > 1]
        kill = set()
        for test in ilengths:
            for dup in dups:
                values = set([test[x] for x in dup])
                if len(values) > 1:
                    kill.add(test)
        ilengths -= kill

    def icapture_values(self, ir, lengths):
        result = []
        shift = 0
        for length in lengths:
            result.append((length, (ir >> shift) & ((1 << length) - 1)))
            shift += length
        return tuple(result)

    def constrain_parts(self, captureset):
        for index, part in enumerate(self):
            if len(captureset) <= 1:
                break
            possible = part.possible_ir
            if not possible:   # Unknown part
                continue
            kill = set()
            for possibility in captureset:
                if possibility[index] not in possible:
                    kill.add(possibility)
            captureset -= kill

    def updateparts(self, captureinfo):
        assert len(self) == len(captureinfo)
        for index, (part, capture) in enumerate(reversed(zip(self, captureinfo))):
            length, value = capture
            oldstr = part.ir_capture
            part.ir_capture = ('{0:0%db}' % length).format(value)
            if not oldstr:
                continue
            if capture in part.possible_ir:
                continue
            print "Warning: Expected IR capture of %s for part at JTAG chain index %d:\n    %s" % (oldstr, index, str(part))

    def add_bypass_info(self):
        ''' Decorate each part with information about its location in the chain.
        '''
        BypassInfo = collections.namedtuple('BypassInfo', 'prev_ir prev_dr next_ir next_dr')
        prev_ir = 0
        prev_dr = 0
        next_ir = len(''.join(part.ir_capture for part in self))
        next_dr = len(self)
        for part in self:
            my_irlen = len(part.ir_capture)
            next_ir -= my_irlen
            next_dr -= 1
            part.bypass_info = BypassInfo(prev_ir * '1', prev_dr * '0', next_ir * '1', next_dr * '0')
            prev_ir += my_irlen
            prev_dr += 1

    def __str__(self):
        result = ['', 'JTAG Chain information', '']
        for i, part in enumerate(self):
            result.append('   #%d - %s' % (i, part))
        result.append('')
        return '\n'.join(result)
