'''
This module provides the Bus32 class.

The Bus32 class provides higher-level generic functionality on top of a low-level
driver that knows how to access a particular bus.  The class provides the
following services:

- Allows reads and writes with single or multiple bytes, halfwords, or words
- Handles alignment issues using ctypes packed union
- Sizes of all read/write requests to lower-level drivers will be powers of 2
- Sizes of all read/write requests to lower-level drivers will be kept <= max_bytes
- Read/write requests to lower-level drivers will not cross addr_align page boundaries
  (unless they are aligned to addr_align and are multiples of addr_align bytes)
- A write of length 0 can be used to inform lower level to flush data.
- Lower level driver can respond to reads by returning a generator, which does
  not need to return data until Bus32 starts iterating through it.

Client API:

Clients can use the read, readhalf, readbyte, or readstring methods to read
data, and the write, writehalf, writebyte, and writestring methods to write
data.  All of these methods accept an integer address as the first parameter.

readstring requires a byte count parameter, and all the other read methods
will return a single value by default, or an optional count can be provided,
in which case they will return a list.

writestring requires a string parameter (even number of characters) and
all the other write methods can accept either a single integer value or
a list of values.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
import collections
import ctypes
import itertools
from binascii import hexlify, unhexlify

class Bus32(object):
    _cachesize = 256
    _sizemap = {1: ctypes.c_uint8,
                2: ctypes.c_uint16,
                4: ctypes.c_uint32,
                8: ctypes.c_uint64}

    def __init__(self, driver):
        self._queue = collections.deque()
        self._cache = {}
        self._getcache = self._cache.get
        self._union = ctypes.Union
        self._sizeof = ctypes.sizeof
        self._big_endian = driver.big_endian
        self._struct = ctypes.BigEndianStructure if driver.big_endian else ctypes.LittleEndianStructure
        self._addr_align = driver.addr_align
        self._max_words = driver.max_bytes / 4
        self._readsingle = driver.readsingle
        self._readmultiple = driver.readmultiple
        self._writesingle = driver.writesingle
        self._writemultiple = driver.writemultiple

    def _chunkinfo(self, addr, count, size=4):
        ''' For aligned accesses, return "chunks"
            of address space using the following rules:
            - All chunks are powers of 2
            - No chunk crosses an addr_align boundary
              (unless it is aligned to addr_align and
              is multiples of addr_align in length)
            - No chunk is larger than max_words
        '''
        assert not addr & (size-1)
        offset = 0
        addr_align = self._addr_align
        max_words = self._max_words
        while count:
            chunklen = min(count, (-addr % addr_align) / size)
            if not chunklen:
                chunklen = count % (addr_align / size)
                if chunklen != count:
                    chunklen = count - chunklen
            chunklen &= ~(chunklen-1)
            if chunklen > max_words:
                chunklen = max_words
            yield addr, offset, chunklen
            addr += chunklen * size
            count -= chunklen
            offset += chunklen

    def _newremap(self, offset, count, elementsize):
        ''' Return a remap class that is a subclass of ctypes.Union,
            and allows easy alignment conversion between internal
            lists and external bytes/halfwords/words.
        '''
        numbytes = count * elementsize
        elements = (numbytes + elementsize - 1) // elementsize
        prefixbyte = bool((numbytes >= 1) and (-offset & 1))
        numbytes -= prefixbyte
        prefixhalf = bool((numbytes >= 2) and (-offset & 2))
        numbytes -= prefixhalf * 2
        suffixbyte = bool(numbytes & 1)
        suffixhalf = bool(numbytes & 2)
        numwords = numbytes / 4
        class struct1(self._struct):
            _fields_ = (
                    ("elements", self._sizemap[elementsize] * elements),
            )
        class struct2(self._struct):
            _pack_ = 1
            _fields_ = (
                    ("prefixbyte", ctypes.c_uint8  * prefixbyte),
                    ("prefixhalf", ctypes.c_uint16 * prefixhalf),
                    ("words",      ctypes.c_uint32 * numwords),
                    ("suffixhalf", ctypes.c_uint16 * suffixhalf),
                    ("suffixbyte", ctypes.c_uint8  * suffixbyte),
            )
        access = []
        for name, mytype in struct2._fields_:
            trial = mytype()
            length = len(trial)
            if length:
                access.append((name, length, self._sizeof(trial) // length))
        class remap(self._union):
            _anonymous_ = 'ab'
            _fields_ = (
                    ("a", struct1),
                    ("b", struct2),
            )
            def __call__(self, addr):
                for name, length, size in access:
                    yield getattr(self, name), addr, length, size
                    addr += length * size
        return remap

    def _getremap(self, addr, count, elementsize):
        ''' It is expensive creating the remap classes, so
            we cache them.
        '''
        offset = addr & 3
        key = offset, count, elementsize
        remap = self._getcache(key)
        if remap is None:
            remap = self._newremap(offset, count, elementsize)
            queue = self._queue
            if len(queue) > self._cachesize:
                del self._cache[queue.popleft()]
            queue.append(key)
            self._cache[key] = remap
        return remap

    def _writealigned(self, addr, length, data):
        ''' Write aligned words.  If they can be
            written in a single chunk to the driver,
            do so, otherwise stack multiple chunks.
        '''
        info = list(self._chunkinfo(addr, length)) or [(addr, 0, 0)]
        for addr, offset, chunklen in info:
            self._writemultiple(addr, data, offset, chunklen)

    def _writemisaligned(self, remapped):
        ''' Write misaligned data, after remapping it.
        '''
        remapped = list(remapped) or [([], 0, 0, 4)]
        for substruct, addr, length, size in remapped:
            if length == 1:
                self._writesingle(addr, size, substruct[0])
            else:
                assert size == 4
                self._writealigned(addr, length, substruct)

    def _writeany(self, addr, values, size, len=len):
        ''' Write words, halfwords, or bytes
        '''
        try:
            length = len(values)
        except TypeError:
            length = values is not None
            values = [] if values is None else [values]
        if not (addr & (size-1)):
            if length == 1:
                return self._writesingle(addr, size, values[0])
            elif size == 4:
                return self._writealigned(addr, length, values)

        remap = self._getremap(addr, length, size)()
        remap.elements[:] = values
        return self._writemisaligned(remap(addr))

    def write(self, addr, value=None):
        ''' Write a 32 bit value or list of 32 bit values
        '''
        return self._writeany(addr, value, 4)

    def writehalf(self, addr, value=None):
        ''' Write a 16 bit value or list of 16 bit values
        '''
        return self._writeany(addr, value, 2)

    def writebyte(self, addr, value=None):
        ''' Write a byte or list of bytes
        '''
        return self._writeany(addr, value, 1)

    def writestring(self, addr, value):
        ''' Write data from a string.  Optimize the
            number of integer conversions and whether or
            not to invoke the misalignment mechanism.

            TODO: Optimize little-endian performance
        '''
        chars = len(value)
        assert not chars & 1
        length = chars / 2
        if length in (1, 2, 4) and self._big_endian and not (length-1) & addr:
            return self._writesingle(addr, length, int(value, 16))
        remap = self._getremap(addr, length, 1)
        remap = remap.from_buffer_copy(unhexlify(value))
        return self._writemisaligned(remap(addr))

    @staticmethod
    def _readflatten(pieces):
        ''' Single-level flatten iterator
        '''
        for iterator in pieces:
            for item in iterator:
                yield item

    def _readaligned(self, addr, length):
        ''' Read aligned words.  If they can be
            read in a single chunk from the driver,
            do so, otherwise stack multiple chunks.
        '''
        pieces = []
        for addr, offset, length in self._chunkinfo(addr, length):
            pieces.append(self._readmultiple(addr, length))
        return self._readflatten(pieces)

    def _readmisaligned(self, remapped):
        ''' Read misaligned data, then remap it.
        '''
        pieces = []
        for substruct, addr, length, size in remapped:
            if length == 1:
                pieces.append((substruct, self._readsingle(addr, size)))
            else:
                assert size == 4
                pieces.append((substruct, self._readaligned(addr, length)))
        for substruct, generator in pieces:
            substruct[:] = list(generator)

    def _readany(self, addr, count, size):
        ''' Read words, halfwords, or bytes
        '''
        unwrap = count is None
        length = unwrap or count
        aligned = not (addr & (size-1))
        if aligned and length == 1:
            result = self._readsingle(addr, size)
        elif aligned and size == 4:
            result = self._readaligned(addr, length)
        else:
            remap = self._getremap(addr, length, size)()
            self._readmisaligned(remap(addr))
            result = remap.elements
        if unwrap:
            return list(result)[0]
        return list(result)

    def read(self, addr, count=None):
        ''' Read a 32 bit value or list of 32 bit values
        '''
        return self._readany(addr, count, 4)

    def readhalf(self, addr, count=None):
        ''' Read a 16 bit value or list of 16 bit values
        '''
        return self._readany(addr, count, 2)

    def readbyte(self, addr, count=None):
        ''' Read a byte or list of bytes
        '''
        return self._readany(addr, count, 1)

    def readstring(self, addr, length, cache={}):
        ''' Read data and create a string.  Optimize the
            number of format conversions and whether or
            not to invoke the misalignment mechanism.

            TODO: Optimize little-endian performance
        '''
        big_endian = self._big_endian
        if length in (1, 2, 4) and big_endian and not (length-1) & addr:
            return '%%0%dx' % (length*2) % self._readsingle(addr, length).next()
        if not length:
            return ''
        myclass = cache.get(length)
        if myclass is None:
            cache[length] = myclass = ctypes.c_char * length
        mystr = myclass()
        remap = self._getremap(addr, length, 1).from_buffer(mystr)
        self._readmisaligned(remap(addr))
        return hexlify(mystr)
