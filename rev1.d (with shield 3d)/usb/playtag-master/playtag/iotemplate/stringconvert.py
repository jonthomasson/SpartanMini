'''
This module contains code to optimize application of I/O templates for
drivers which expect binary data.  This module handles everything in
strings, including converting TDI integer data from the application into
strings, and extracting TDO integer data for the application from strings.

All the strings are binary, consisting of '1' and '0' characters, and sometimes
'x' to denote variable data and '*' to denote don't care data.

Repository revision 23 contains an earlier version of this code which is
designed for the digilent cable.  It is much shorter (1/3 the size) and
thus perhaps a bit more understandable.  This code has now been generalized
to be able to support the FTDI MPSSE.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
import itertools
from .basexstring import BaseXString

class TemplateStrings(BaseXString):
    ''' This class contains code to help compile device-independent template
        information into device-specific data.  This progresses in stages:
          1) First, long strings are generated for tms, tdi, and tdo.
               - 'x' denotes variable information
               - '*' denotes "don't care" information
               - The only valid characters in the tms string are '0' and '1'
               - The only valid characters in the tdi string are '0', '1', '*', and 'x'
               - The only valid characters in the tdo string are '*' and 'x'.
          2) Then, a device-specific customize_template method is called.  For
             the digilent cable, this does nothing.  For the FTDI cables, this
             will insert commands into the tdi string, and massage the tdo string
             to match expected data coming back.
          3) Then the strings are examined to create values for the tdi_combiner
             and tdo_extractor functions, and a template is created with the
             functions to call to send/receive data from the driver.
          4) Finally, the template is applied (possibly multiple times) to
             send/receive data.
    '''
    tdo_extractor = None

    def get_tdi_converter(self, len=len):
        ''' Create a converter that will eat the input
            variable TDI data integers and create a single
            boolean string with all the data concatenated.

            The original design for the Digilent driver
            just interspersed the format information between
            constant information.  But the FTDI chip doesn't
            necessarily keep bits from a single input value
            together because of the way it handles exiting
            DR_SHIFT or IR_SHIFT, so we just convert all the
            input variables into a single variable string,
            and then merge it with the constant string now.
        '''
        strings = []
        counts = []
        total_bits = 0
        for numbits, index in self.tdi_bits:
            missing = index + 1 - len(counts)
            if missing:
                counts.extend(missing * [0])
            strings.append('{%d[%d]:0%db}' % (index, counts[index], numbits))
            counts[index] += 1
            total_bits += numbits
        strings.reverse()
        format = ''.join(strings).format
        del strings

        def tdi_converter(tdi):
            ''' Dump all the TDI data into one big honking boolean string.
            '''
            lengths = [len(x) for x in tdi]
            if lengths != counts and (counts or sum(lengths)):
                raise ValueError("Expected %s TDI elements; got %s" % (counts, lengths))
            tdistr = format(*tdi)
            assert len(tdistr) == total_bits, (total_bits, len(tdistr))
            return tdistr
        return tdi_converter

    def get_tdi_combiner(self, len=len, slice=slice):
        ''' Create a combiner function that will use the
            tdi_converter and the tdi_string to merge the
            constant and variable portions of the TDI
            data together.
        '''
        strings = self.x_splitter(self.tdi_xstring)
        first_string = strings[0]
        const_str = strings[2::2]
        bitlens = (len(x) for x in itertools.islice(strings, 1, None, 2))
        nextindex = 0
        slices = []
        for x in bitlens:
            index = nextindex
            nextindex = index + x
            slices.append(slice(index, nextindex))
        assert len(slices) == len(const_str)
        del strings, bitlens

        tdi_converter = self.get_tdi_converter()
        izip = itertools.izip
        join = ''.join

        def tdi_combiner(tdi):
            ''' Return small easily digestible string chunks.
                Let other devices have their way with them.
            '''
            yield first_string
            variables = tdi_converter(tdi)
            for var, const in izip(slices, const_str):
                yield variables[var]
                yield const
        return tdi_combiner

    def get_tdo_extractor_slices(self, len=len, slice=slice):
        ''' This function is somewhat complicated by support for
            things like the FTDI driver, where the input bits for
            a word might not be all together.

            The output of this function is two lists of slices.
            The first list, "keep", defines the slices to keep
            from the string coming from the driver.  These slices
            are then concatenated together before extracting each
            tdo value individually using the "extract" list.
            To reduce the number of slice operations involved,
            the "keep" list will keep returned data between valid
            words.  In some cases, this might mean keeping all
            the data.
        '''
        strings = self.x_splitter(self.tdo_xstring)
        constbits = (len(x) for x in itertools.islice(strings, 0, None, 2))
        varbits = (len(x) for x in itertools.islice(strings, 1, None, 2))
        wordbits = list(self.tdo_bits)
        source_index = 0
        extract_index = 0
        collected = 0
        keep_start = [None]
        keep_stop = []
        extract = []
        for inc, size in itertools.izip(constbits, varbits):
            source_index += inc
            if collected:
                keep_start.append(source_index)
            else:
                extract_index += inc
            source_index += size
            collected += size
            while collected and collected >= wordbits[-1]:
                length = wordbits.pop()
                collected -= length
                extract.append(slice(extract_index, extract_index + length))
                extract_index += length
            if collected:
                keep_stop.append(source_index)
        keep_stop.append(None)
        keep = [slice(x,y) for (x,y) in itertools.izip(keep_start, keep_stop)]
        extract.reverse()
        return keep, extract

    def get_tdo_extractor(self, len=len, int=int):
        ''' Define a function that will extract a list of integers
            from the TDO string from the driver.
        '''
        keep, extract = self.get_tdo_extractor_slices()
        sourcesize = len(self.tdo_xstring)
        join=''.join
        def tdo_extractor(s):
            s = ''.join(s)
            assert len(s) == sourcesize, (len(s), sourcesize)
            s = join(s[x] for x in keep)
            return (int(s[x], 2) for x in extract)
        return tdo_extractor

    def get_xfer_func(self, join=''.join):
        self.tdi_xstring = self.tdi_xstring.replace('*', '0')
        tms_template = self.tms_string
        tditostr = self.get_tdi_combiner()

        if self.tdo_bits:
            tdofromstr = self.get_tdo_extractor()
            def func(driver, tdi_array):
                tdostr = driver(tms_template, join(tditostr(tdi_array)), tdofromstr)
                return tdofromstr(tdostr)
        else:
            def func(driver, tdi_array):
                driver(tms_template, join(tditostr(tdi_array)), None)

        vars(self).clear()
        return func
