import itertools
from ctypes import c_ulonglong, byref
from .d2xx import FtdiDevice
from .mpsse_template import MpsseTemplate

def debug_dump(f, title, data, numbytes):
    print >> f, title,
    for i in range(numbytes):
        print >> f, '%02x' % ((data[i/8] >> ((i % 8) * 8)) & 0xFF),
    print >> f

class Jtagger(MpsseTemplate.mix_me_in()):

    def __init__(self, devname, maxbits=2**22):
        driver = FtdiDevice(devname)
        driver.setspeed(15e6)
        size = (maxbits + 63) / 64
        source = (size * 2 * c_ulonglong)()  # Both TMS and TDI go here
        dest = (size * c_ulonglong)()
        count = driver.DWORD()
        self.wparams = driver.Write, len(source) * 64, source, byref(source), count, byref(count), driver.debug
        self.rparams = driver.Read, len(dest) * 64, dest, byref(dest)

    def __call__(self, sendstr, numbits, rcvlen, formatter = '{0:064b}'.format,
                          int=int, len=len, join=''.join, tee=itertools.tee,
                          chain=itertools.chain, izip=itertools.izip, xrange=xrange):
        '''  Passed tms/tdi info.  Returns tdo.
             All these are strings of '0' and '1'.
             First bit sent is the last bit in the string...
        '''
        if not numbits:
            return
        sendstr = join(sendstr)
        assert len(sendstr) == numbits
        write, sourcelen, source, sourceref, count, countref, debug = self.wparams
        assert not numbits & 7
        numbytes = (numbits + 7) / 8
        numints = (numbytes + 7) / 8
        start, stop = tee(xrange(numbits - 64, 0, -64))
        slices = izip(chain(start, (None,)), chain((None,), stop))
        source[:numints] = [int(sendstr[x:y],2) for x,y in slices]
        if debug:
            debug_dump(debug, 'xmt', source, numbytes)
        write(sourceref, numbytes, countref)
        assert count.value == numbytes
        if not rcvlen:
            return
        numbits = rcvlen
        assert not numbits & 7
        read, destlen, dest, destref = self.rparams
        assert numbits <= destlen, (numbits, destlen)
        numbytes = (numbits + 7) / 8
        numints = (numbytes + 7) / 8
        read(destref, numbytes, countref)
        if debug:
            debug_dump(debug, 'rcv', dest, numbytes)
        assert count.value == numbytes
        allbits = [formatter(x) for x in reversed(dest[:numints])]
        allbits[0] = allbits[0][numints * 64 - numbits:]
        return allbits
