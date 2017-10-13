'''
This module provides a driver for the Digilent USB-JTAG cable

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
import sys
from itertools import izip
from ctypes import c_ubyte, c_char, c_uint32, c_int, c_ulonglong, POINTER, c_char_p, CDLL, byref, cast, Structure
import atexit

from ...iotemplate.stringconvert import TemplateStrings

test = __name__ == '__main__'
profile = False

HIF = DWORD = c_uint32
BOOL = c_int
DTP = DWORD
BYTE = c_ubyte
STRING = c_char_p

class DVC(Structure):
    _fields_ = [
        ('szName', c_char * 64),
        ('szConn', c_char * 272),  # Round up to nearest 16
        ('dtp', DTP),
    ]

if 'win' in sys.platform:
    Dmgr = CDLL('dmgr.dll')
    Djtg = CDLL('djtg.dll')
else:
    Djtg = CDLL('/usr/local/lib64/digilent/adept/libdjtg.so')
    Dmgr = CDLL('/usr/local/lib64/digilent/adept/libdmgr.so')

DmgrEnumDevices = Dmgr.DmgrEnumDevices
DmgrEnumDevices.restype = BOOL
DmgrEnumDevices.argtypes = [POINTER(c_int)]
DmgrGetDvc = Dmgr.DmgrGetDvc
DmgrGetDvc.restype = BOOL
DmgrGetDvc.argtypes = [c_int, POINTER(DVC)]

DmgrOpen = Dmgr.DmgrOpen
DmgrOpen.restype = BOOL
DmgrOpen.argtypes = [POINTER(HIF), STRING]
DmgrClose = Dmgr.DmgrClose
DmgrClose.restype = BOOL
DmgrClose.argtypes = [HIF]

DjtgEnable = Djtg.DjtgEnable
DjtgEnable.restype = BOOL
DjtgEnable.argtypes = [HIF]
DjtgDisable = Djtg.DjtgDisable
DjtgDisable.restype = BOOL
DjtgDisable.argtypes = [HIF]

DjtgPutTmsTdiBits = Djtg.DjtgPutTmsTdiBits
DjtgPutTmsTdiBits.restype = BOOL
DjtgPutTmsTdiBits.argtypes = [HIF, POINTER(BYTE), POINTER(BYTE), DWORD, BOOL]

DjtgGetSpeed = Djtg.DjtgGetSpeed
DjtgGetSpeed.restype = BOOL
DjtgGetSpeed.argtypes = [HIF, POINTER(DWORD)]
DjtgSetSpeed = Djtg.DjtgSetSpeed
DjtgSetSpeed.restype = BOOL
DjtgSetSpeed.argtypes = [HIF, DWORD, POINTER(DWORD)]

def check(func, *params):
    result = func(*params)
    if not result:
        raise IOError("Error from digilent driver")

def NumDevices():
    myint = c_int()
    check(DmgrEnumDevices, byref(myint))
    return myint.value

def DevName(index):
    dvc = DVC()
    check(DmgrGetDvc, index, byref(dvc))
    return dvc.szName

def showdevs():
    numdevs = NumDevices()
    print "\n%d devices found:\n" % numdevs
    for index in range(numdevs):
        print '    ', DevName(index)
    print

class Jtagger(HIF, TemplateStrings.mix_me_in()):
    isopen = False
    isenabled = False
    def __init__(self, UserConfig, maxbits=2**22):
        devname = UserConfig.CABLE_NAME = UserConfig.CABLE_NAME or 'DCabUsb'
        try:
            devname + ''
        except TypeError:
            UserConfig.error("Expected string for CABLE_NAME, not %s" % repr(devname))
        size = (maxbits + 63) / 64
        source = (size * 2 * c_ulonglong)()  # Both TMS and TDI go here
        dest = (size * c_ulonglong)()
        count = DWORD()
        overlap = BOOL()
        overlap.value = False
        self.maxbits = maxbits
        self.rparams = cast(source, POINTER(BYTE)), cast(dest, POINTER(BYTE)), count, overlap
        self.wparams = cast(source, POINTER(BYTE)), None, count, overlap
        self.source = source
        self.dest = dest
        self.count = count
        self.closer = DmgrClose
        self.disabler = DjtgDisable
        check(DmgrOpen, byref(self), devname)
        self.isopen = True
        atexit.register(self.__del__)
        check(DjtgEnable, self)
        self.isenabled = True

    def __del__(self, check=check):
        if self.isopen:
            self.isopen = False
            if self.isenabled:
                self.isenabled = False
                check(self.disabler, self)
            check(self.closer, self)

    def getspeed(self):
        myint = DWORD()
        check(DjtgGetSpeed, self, byref(myint))
        return myint.value

    def setspeed(self, newspeed):
        myint = DWORD()
        check(DjtgSetSpeed, self, newspeed, byref(myint))
        return myint.value

    def __call__(self, tms, tdi, usetdo, formatter = '{0:064b}'.format, int=int, len=len):
        '''  Passed tms, tdi.  Returns tdo.
             All these are strings of '0' and '1'.
             First bit sent is the last bit in the string...
        '''
        numbits = len(tms)
        if not numbits:
            return
        assert 0 < numbits == len(tdi) <= self.maxbits
        numints = (numbits + 63) / 64
        leftpad = numints * 64 - numbits
        allbits = [leftpad * 2 * '0']
        extend = allbits.extend
        for x in izip(tms, tdi):
            extend(x)
        allbits = ''.join(allbits)
        assert len(allbits) == numints * 128
        allbits = [int(allbits[i:i+64],2) for i in xrange(len(allbits) - 64, -1, -64)]
        self.source[:len(allbits)] = allbits
        self.count.value = numbits
        if usetdo:
            if not profile or numbits < 1000:
                check(DjtgPutTmsTdiBits, self, *self.rparams)
            allbits = [formatter(x) for x in reversed(self.dest[:numints])]
            allbits[0] = allbits[0][leftpad:]
            return allbits
        else:
            if not profile or numbits < 1000:
                check(DjtgPutTmsTdiBits, self, *self.wparams)

__all__ = 'Jtagger showdevs DevName NumDevices'.split()
