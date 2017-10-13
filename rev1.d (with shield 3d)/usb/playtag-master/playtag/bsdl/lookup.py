#!/usr/bin/env python
'''
Look up a JTAG ID in the database

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

import os

root = os.path.dirname(__file__)

def readfile(fname):
    ''' Strip #-delimited comments, and then split each
        line into tokens, and yield each line.
    '''
    f = open(fname, 'rb')
    data = f.read()
    f.close()
    for line in data.splitlines():
        line = line.split('#',1)[0].split()
        if line:
            yield line

def expand_x():
    ''' Take a string that has x's in it, and return
        multiple strings, replacing each x with both
        a 0 and a 1.

        Recurse without incurring a globals() lookup
        on each recursion.
    '''
    def expand_x(s):
        if 'x' in s:
            a, b = s.rsplit('x', 1)
            for a in expand_x(a):
                s = (a, b)
                yield '0'.join(s)
                yield '1'.join(s)
        else:
            yield s
    return expand_x
expand_x = expand_x()

class PartParameters(object):
    ''' Describes the parameters of an abstract part.
        More than one part on the chain can share the
        same PartParameters, so no system-device-specific
        information should be stored here.
    '''
    manufacturer = None  # Can override value from file here

    def __init__(self, idcode='', ir_capture='', name='(unknown part)'):
        if not isinstance(idcode, str):
            value, mask = idcode
            value, mask = '{0:032b} {1:032b}'.format(value, mask).split()
            idcode = ''.join((x if y == '1' else'x') for (x,y) in zip(value, mask))
        self.idcode = idcode
        self.ir_capture = ir_capture
        self.name = name
    base_init = __init__

class PartInfo(object):
    ''' Each instantiation of PartInfo represents an actual
        physical part in a chain, and can be decorated by
        clients with information they need.
    '''
    partfile = os.path.join(root, 'data', 'partindex.txt')
    mfgfile = os.path.join(root, 'data', 'manufacturers.txt')
    partcache = {}
    mfgcache = {}

    _possible_ir = None

    @classmethod
    def addparts(cls, partlist, int=int, expand_x=expand_x):
        partcache = cls.partcache

        for part in partlist:
            for idcode in expand_x(part.idcode):
                partcache[int(idcode, 2)] = part

    @classmethod
    def addmfgs(cls, mfginfo, int=int):
        mfgcache = cls.mfgcache
        for line in (iter(x) for x in mfginfo):
            index = int(line.next(), 2)
            mfgcache[index] = ' '.join(line)

    @classmethod
    def initcaches(cls, int=int):
        cls.addparts(PartParameters(*x) for x in readfile(cls.partfile))
        cls.addmfgs(readfile(cls.mfgfile))

    def __init__(self, index, unknown=PartParameters()):
        try:
            index = int(index, 2)
        except TypeError:
            pass
        parameters = self.partcache.get(index, unknown)
        self.idcode = index
        self.parameters = parameters
        self.name = parameters.name
        self.ir_capture = parameters.ir_capture
        self.manufacturer = parameters.manufacturer
        if self.manufacturer is None:
            mfgid = (index >> 1) & ((1 << 11) - 1)
            self.manufacturer = self.mfgcache.get(mfgid, '(unknown manufacturer)')

    @property
    def possible_ir(self, int=int):
        result = self._possible_ir
        if result is not None:
            return result
        ir_capture = self.ir_capture
        if ir_capture:
            size = len(ir_capture)
            result = set((size, int(x, 2)) for x in expand_x(ir_capture))
        else:
            result = set()
        self._possible_ir = result
        return result

    def __str__(self):
        idcode = self.idcode
        if idcode:
            idcode = '{0:032b}'.format(idcode)
            idcode = '_'.join((idcode[0:4], idcode[4:20], idcode[20:31], idcode[31]))
        return '%s %s (ir_capture = %s, idcode=%s)' % (self.manufacturer,
                    self.name, repr(self.ir_capture), repr(idcode))

PartInfo.initcaches()

if __name__ == '__main__':
    import sys
    for item in sys.argv[1:]:
        print '%s -- %s' % (item, str(PartInfo(item)))
