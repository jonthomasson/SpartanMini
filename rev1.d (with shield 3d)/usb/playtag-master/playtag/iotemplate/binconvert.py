'''
This module contains code to optimize application of I/O templates for
drivers which expect binary data.  This module is based on stringconvert,
but is modified to use ctypes structures for the transfer, instead
of converting to strings and back on every I/O transaction.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
from itertools import islice, izip
import itertools
from .stringconvert import TemplateStrings


def initial_default(AllFields, default):
    ''' A closure that is a factory function
        for our structure with the correct default.
    '''
    init = AllFields.from_buffer_copy
    del AllFields
    def func():
        return init(default)
    return func

def makeunion(fieldinfo, default):
    ''' Create a union given a list of two lists of fields,
        and a default value.
    '''
    bytetype = ctypes.c_uint8 * len(default)
    class FieldA(ctypes.Structure):
        _fields_ = fieldinfo[0]
    class FieldB(ctypes.Structure):
        _pack_ = 1
        _fields_ = fieldinfo[1]
    class AllFields(ctypes.Union):
        _anonymous_ = 'ab'
        _fields_ = [('a', FieldA),
                    ('b', FieldB),
                    ('bytes', bytetype),
                    ]
    get_default = initial_default(AllFields, bytetype(*default))
    del fieldinfo, default, bytetype, FieldA, FieldB
    return AllFields, get_default

class BinTemplate(BaseXString):
    ''' This class contains code to help compile device-independent template
        information into device-specific data.  This progresses in stages:
          1) First, long strings are generated for tms, tdi, and tdo.
               - 'x' denotes variable information
               - '*' denotes "don't care" information
               - The only valid characters in the tms string are '0' and '1'
               - The only valid characters in the tdi string are '0', '1', '*', and 'x'
               - The only valid characters in the tdo string are '*' and 'x'.
             This first step is done by the BaseXString class functions.
          2) Then, a device-specific customize_template method is called.  This
             class expects that TMS will be consumed and the TDI and TDO strings
             will be modified to insert commands and spacers for extra expected data.
          3) Then the strings are examined to create ctypes class templates.
          4) Finally, the template is applied (possibly multiple times) to
             send/receive data.
    '''

    inttype = ctypes.c_uint64
    halfinttype = ctypes.c_uint32
    intbits = 64
    resolution = intbits / 2

    def hw_fields(self, len=len):
        ''' Generate tuples of offset/length pairs based on
            cable driver dependent information from the TDI
            string.
        '''
        total_offset = 0
        total_bitlen = 0
        lengths = [len(x) for x in self.x_splitter(self.tdi_xstring)]
        lengths.reverse()
        for offset, bitlen in (izip(islice(lengths, 0, None, 2),
                               izip(islice(lengths, 1, None, 2)):
            total_offset += offset
            yield total_offset, bitlen
            total_offset += bitlen
            total_bitlen += bitlen
        assert total_offset + len(strings[0]) == len(self.tdi_xstring)
        self.hw_bitlen = total_bitlen


    def sw_fields(self, len=len):
        ''' Generate tuples of (numbits, index, subindex) based on
            expected TDI values from higher layer when the template
            is applied.
        '''
        counts = []
        for numbits, index in self.tdi_bits:
            missing = index + 1 - len(counts)
            if missing:
                counts.extend(missing * [0])
            yield numbits, index, counts[index]
            counts[index] += 1
            total_bits += numbits
        self.sw_bitlen = total_bitlen
        self.tdi_counts = counts

    def combine_fields(self):
        ''' Combine the cable-driver hardware-specific fields
            with the upper layer TDI information fields to
            determine how to extract TDI information and
            where to put it in our structure.
            Return tuples of
               ( hw_field_name,    # unique name
                 hw_offset,        # Bit offset into TDI output string
                 numbits,          # Number of bits in this (sub)field
                 sw_index,         # first index into TDI data structure
                 sw_subindex,      # second index into TDI data structure
                 sw_shift)         # distance to shift TDI input
        '''
        intbits = self.intbits
        resolution = self.resolution
        sw_fields = list(self.sw_fields)
        sw_field_index = 0
        sw_bits = 0
        hw_field_index = 0
        for hw_offset, hw_bits in self.hw_fields:
            while hw_bits:
                if not sw_bits:
                    sw_bits, sw_index, sw_subindex = sw_fields[sw_field_index]
                    sw_field_index += 1
                    sw_shift = 0
                take = min(hw_bits, sw_bits, intbits - hw_offset % resolution)
                hw_field_name = 'field%04d' % hw_field_index
                hw_field_index += 1
                yield hw_field_name, hw_offset, take, sw_index, sw_subindex, sw_shift
                hw_offset += take
                hw_bits -= take
                sw_bits -= take
                sw_shift += take
        assert sw_field_index == len(sw_fields)
        assert self.hw_bitlen == self.sw_bitlen

    def structfields(self, fieldlists, index):
        ''' Normalize one of our fieldlists
            into a format that ctypes expects for _fields_.
        '''
        inttype = self.inttype
        intbits = self.intbits
        if index:
            yield ('offset', halfinttype, self.resolution)
        offset = 0
        dummycount = 0
        for fieldname, fieldoffset, fieldbits in fieldlists[index]:
            delta = fieldoffset - offset
            firstdummy = min(delta, -offset % intbits)
            for dummybits in (firstdummy, delta - firstdummy):
                if dummybits:
                    yield 'dummy%d' % dummycount, inttype, dummybits
            yield fieldname, inttype, fieldbits
            offset = fieldoffset + fieldbits

    def setupfields(self):
        ''' Take combined hw/sw field info from combine_fields() and
            split it into hw structure field info, and sw conversion
            info.  Then normalize the hw structure field info,
            get our default output value (non-variable information),
            and create our ctypes structure.  Finally, modify
            the sw conversion info to directly access the correct
            setter inside the ctypes structure.
        '''
        resolution = self.resolution
        fieldinfo = [], []
        convert = []
        for (hw_field_name, hw_offset, numbits,
                sw_index, sw_subindex, sw_shift) in self.combine_fields():
            convert.append((hw_field_name, sw_index, sw_subindex, sw_shift))
            fieldsel = hw_offset & resolution
            fieldinfo[bool(fieldsel)].append((hw_field_name, hw_offset - fieldsel, numbits))
        fieldinfo = [list(self.structfields(fieldinfo, x)) for x in range(len(fieldinfo))]
        default = self.tdi_xstring.replace('x', '0')
        assert not len(default) % 8
        default = [int(default[x:x+8] for x in range(len(default)-8, -1, -8)]
        AllFields, get_default = makeunion(fieldinfo, default)

        convert = [(getattr(AllFields, hw_field_name).__set__, sw_index, sw_subindex, sw_shift)
                       for (hw_field_name, sw_index, sw_subindex, sw_shift) in convert]
        return get_default, convert


    def get_tdi_builder(self, len=len, sum=sum):
        ''' Create a closure function that will use
            the information from setupfields() to
            take TDI input from a higher layer and create
            the data structure the driver needs.
        '''
        get_default, convert = self.setupfields()
        counts = self.tdi_counts
        def tdi_combiner(tdi):
            lengths = [len(x) for x in tdi]
            if lengths != counts and (counts or sum(lengths)):
                raise ValueError("Expected %s TDI elements; got %s" % (counts, lengths))
            x = get_default()
            for (setter, index, subindex, shift) in convert:
                setter(x, tdi[index][subindex] >> shift)
            return x
        return tdi_builder
