'''
Abstractions that allow easy access to hardware registers.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
class HexNum(long):
    def __new__(cls, value, size=32):
        if size < 4:
            return long(value)
        self = long.__new__(cls, value)
        self.size = (size + 3) / 4
        return self

    def __repr__(self):
        return '0x%%0%dx' % self.size % self
    def __str__(self):
        return '0x%%0%dx' % self.size % self

class Block(object):
    offset = 0
    size = 0
    def __new__(cls, baseaddr, access):
        self = object.__new__(Block)
        self.block = cls
        self.access = access
        self.baseaddr = baseaddr + cls.offset
        self._read = access.read
        self._write = access.write
        self._length = cls.size / 4
        return self

    def __getattr__(self, name):
        reg = getattr(self.block, name)
        return reg(self.baseaddr, self.access)

    def _getslice(self, index):
        if isinstance(index, slice):
            start, stop, step = index.start, index.stop, index.step
            assert step is None
            islist = True
        else:
            start = stop = index
            islist = False
        length = self._length
        if start is None:
            start = 0
        elif start < 0:
            start = length - start
        if stop is None:
            stop = length
        elif stop < 0:
            stop = length - stop
        assert 0 <= start <= stop <= length, (start, stop, length)
        return start + self.baseaddr, stop - start, islist

    def __getitem__(self, index):
        addr, length, islist = self._getslice(index)
        if islist:
            return [HexNum(x) for x in self._read(addr, length)]
        return HexNum(self._read(addr))

    def __setitem__(self, index, value):
        addr, length, islist = self._getslice(index)
        try:
            vlength = len(value)
        except TypeError:
            assert not islist
        else:
            assert islist and length == vlength, (islist, length, vlength)
        self._write(addr, value)

    def __len__(self):
        return self._length

class BlockArray(Block):
    count = 1
    def __new__(cls, baseaddr, access):
        stride = cls.stride
        count = cls.count
        return tuple(Block.__new__(cls, baseaddr + cls.size * x, access) for x in range(cls.count))

class Register(object):
    def __new__(cls, baseaddr, access):
        self = object.__new__(Register)
        self._fields = vars(cls)
        self._read = access.read
        self._write = access.write
        self._addr = baseaddr + cls.offset
        self.value = 0
        return self

    @staticmethod
    def _startstop(index):
        if isinstance(index, slice):
            start, stop, step = index.start, index.stop, index.step
            assert step is None
            if start is None:
                start = 31
            if stop is None:
                stop = 0
        elif isinstance(index, (list, tuple)):
            start, stop = index
        else:
            start = stop = index
        mask = (2 << start) - (1 << stop)
        shift = stop
        return shift, mask, start-stop+1

    def __getitem__(self, index):
        shift, mask, size = self._startstop(index)
        return HexNum((self.value & mask) >> shift, size)

    def __setitem__(self, index, value):
        shift, mask, size = self._startstop(index)
        self.value = HexNum((self.value & ~mask) | ((value << shift) & mask))

    def __getattr__(self, name):
        if name[0].isupper():
            return self[self._fields[name]]
        raise AttributeError

    def __setattr__(self, name, value):
        if name[0].isupper():
            self[self._fields[name]] = value
        vars(self)[name] = value

    def load(self):
        self.value = HexNum(self._read(self._addr))
        return self

    def store(self, value=None):
        if value is not None:
            self.value = value
        self._write(self._addr, self.value)
        return self

    def __repr__(self):
        fields = []
        for x, y in self._fields.iteritems():
            if not x[0].isupper():
                continue
            try:
                y = y[0]
            except:
                pass
            fields.append((y,x))
        fields = [x[1] for x in reversed(sorted(fields))]
        result = [str(self.value), '']
        for f in fields:
            result.append('     %s = %s' % (f, getattr(self, f)))
        result.append('')
        return '\n'.join(result)
    def __str__(self):
        return repr(self)
