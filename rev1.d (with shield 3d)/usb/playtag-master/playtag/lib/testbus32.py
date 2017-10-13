#!/usr/bin/env python

import random
import itertools

from bus32 import Bus32

exhaustive = False
randomized = True

def run(izip=itertools.izip, islice=itertools.islice):

    randomdata = range(256)
    if randomized:
        for i in range(10):
            random.shuffle(randomdata)
    if not exhaustive:
        randomdata = randomdata[:128]

    wordsize = 4
    class Driver(set):
        flushing = False
        def __init__(self):
            self.addr_align = alignment
            self.max_bytes = maxbytes

        def readsingle(self, addr, size):
            assert size <= wordsize
            assert not addr & (size-1)
            result = 0
            addr = range(addr, addr + size)
            if not bigendian:
                addr.reverse()
            for addr in addr:
                result = result * 256 + randomdata[addr]
            yield result

        def writesingle(self, addr, size, data):
            assert size <= wordsize
            assert not addr & (size-1)
            addr = range(addr, addr + size)
            if bigendian:
                addr.reverse()
            for addr in addr:
                self.add((addr, data & 0xff))
                data >>= 8

        def readmultiple(self, addr, length):
            assert length > 0
            assert not addr % wordsize
            assert length <= maxbytes
            if (length | addr) % alignment:
                assert length + (addr % alignment) <= alignment
            read = self.readsingle
            for addr in xrange(addr, addr + length * wordsize, wordsize):
                for data in read(addr, wordsize):
                    yield data

        def writemultiple(self, addr, data, offset, length):
            assert (length <= 0) == self.flushing
            assert not addr % wordsize
            assert length <= maxbytes
            if (length | addr) % alignment:
                assert length + (addr % alignment) <= alignment
            write = self.writesingle
            addr = itertools.count(addr, wordsize)
            data = itertools.islice(data, offset, offset + length)
            for addr, data in itertools.izip(addr, data):
                write(addr, wordsize, data)


    def testreads(starta, length):
        expected = randomdata[starta:starta + length]
        actual = list(bus.readbyte(starta, length))
        assert expected == actual, (expected, actual, starta, length)
        expecteds = ''.join('%02x' % x for x in expected)
        actuals = bus.readstring(starta, length)
        assert expecteds == actuals, (expecteds, actuals, starta, length)
        if length & 1:
            if length == 1:
                actual = [bus.readbyte(starta)]
                assert expected == actual, (expected, actual, starta, length)
            return
        msb, lsb = (0, 1) if bigendian else (1, 0)
        expected = [x * 256 + y for (x,y) in izip(islice(expected, msb, None, 2), islice(expected, lsb, None, 2))]
        actual = list(bus.readhalf(starta, length/2))
        assert expected == actual, (expected, actual, starta, length)
        if length & 2:
            if length == 2:
                actual = [bus.readhalf(starta)]
                assert expected == actual, (expected, actual, starta, length)
            return
        expected = [x * 65536 + y for (x,y) in izip(islice(expected, msb, None, 2), islice(expected, lsb, None, 2))]
        actual = list(bus.read(starta, length/4))
        assert expected == actual, (expected, actual, starta, length)
        if length == 4:
            actual = [bus.read(starta)]
            assert expected == actual, (expected, actual, starta, length)

    def testwrites(starta, length):
        addresses = range(starta, starta + length)
        data = [randomdata[x] for x in addresses]
        expected = [(x,y) for (x,y) in zip(addresses, data)]
        driver.clear()
        bus.writebyte(starta, data)
        actual = sorted(driver)
        assert expected == actual, (expected, actual, starta, length)
        datas = ''.join('%02x' % x for x in data)
        driver.clear()
        bus.writestring(starta, datas)
        actual = sorted(driver)
        assert expected == actual, (expected, actual, starta, length)
        if length & 1:
            if length == 1:
                driver.clear()
                bus.writebyte(starta, data[0])
                actual = sorted(driver)
                assert expected == actual, (expected, actual, starta, length)
            return
        msb, lsb = (0, 1) if bigendian else (1, 0)
        data = [x * 256 + y for (x,y) in izip(islice(data, msb, None, 2), islice(data, lsb, None, 2))]
        driver.clear()
        bus.writehalf(starta, data)
        actual = sorted(driver)
        assert expected == actual, (expected, actual, starta, length)
        if length & 2:
            if length == 2:
                driver.clear()
                bus.writehalf(starta, data[0])
                actual = sorted(driver)
                assert expected == actual, (expected, actual, starta, length)
            return
        data = [x * 65536 + y for (x,y) in izip(islice(data, msb, None, 2), islice(data, lsb, None, 2))]
        driver.clear()
        bus.write(starta, data)
        actual = sorted(driver)
        assert expected == actual, (expected, actual, starta, length)
        if length == 4:
            driver.clear()
            bus.write(starta, data[0])
            actual = sorted(driver)
            assert expected == actual, (expected, actual, starta, length)

    def testall():
        lasta = len(randomdata)
        driver.flushing = True
        for starta in range(lasta):
            for value in (None, []):
                bus.write(starta, value)
                bus.writehalf(starta, value)
                bus.writebyte(starta, value)
            bus.writestring(starta, '')
            assert bus.read(starta, 0) == [], starta
            assert bus.readhalf(starta, 0) == [], starta
            assert bus.readbyte(starta, 0) == [], starta
            assert bus.readstring(starta, 0) == '', starta
        driver.flushing = False
        assert not driver

        for length in range(1, lasta+1):
            for starta in range(lasta-length):
                testreads(starta, length)
                testwrites(starta, length)

    for alignment in ((16, 32) if exhaustive else (16,)):
        for maxbytes in ((32, 128) if exhaustive else(32,)):
            for bigendian in (True, False):
                driver = Driver()
                driver.big_endian = bigendian
                bus = Bus32(driver)
                testall()

run()
