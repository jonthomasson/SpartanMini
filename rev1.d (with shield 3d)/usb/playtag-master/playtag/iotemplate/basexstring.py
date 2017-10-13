'''
This module contains code to optimize application of I/O templates for
drivers which expect binary data.  The BaseXString class converts
the device-independent templates into string data (which are still
relatively device-independent) and then allows device-specific
manipulation on the strings and other device-specific optimization.

This class is subclassed -- it contains useful functions for performing
this task, but is not complete.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
import re
from ..iotemplate import TDIVariable

class BaseXString(object):
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

    x_splitter = re.compile('(x+)').split

    def set_tdi_xstring(self, tdi_template, isinstance=isinstance, str=str, len=len, TDIVariable=TDIVariable):
        ''' Create a string of '0', '1', and 'x' based on the
            template TDI.  This string might later be modified by
            driver-specific code to insert commands for the JTAG
            cable.
        '''
        self.tdi_bits = tdi_bits = []
        strings = []
        addstring = strings.append
        addbits = tdi_bits.append
        for numbits, value in tdi_template:
            if isinstance(value, TDIVariable):
                addbits((numbits, value.index))
                value = numbits * 'x'
            elif not isinstance(value, str):
                if value < 0:
                    assert value == -1, value
                    value = (1 << numbits) - 1
                value = '{0:0{1}b}'.format(value, numbits)
            assert len(value) == numbits, (value, numbits)
            addstring(value)
        strings.reverse()
        self.tdi_xstring = ''.join(strings)
        assert len(self.tdi_xstring) == self.transaction_bit_length

    def set_tdo_xstring(self, tdo_template):
        ''' Sets '*' for bit positions where we do not require input,
            or 'x' for those positions requiring input.  This string
            might later be modified by driver-specific code before
            being used.
        '''
        self.tdo_bits = [x[1] for x in tdo_template]
        #self.tdo_bits.reverse() # Check later if works right with Digilent
        if not tdo_template:
            self.tdo_xstring = self.transaction_bit_length * '*'
            return
        strings = []
        strloc = 0
        prevlen = 0
        total = 0
        for offset, slicelen in tdo_template:
            offset -= prevlen
            assert offset >= 0
            strings.append('*' * offset)
            strings.append('x' * slicelen)
            prevlen = slicelen
            total += offset + slicelen
        strings.append('*' * (self.transaction_bit_length - total))
        strings.reverse()
        self.tdo_xstring = ''.join(strings)
        assert len(self.tdo_xstring) == self.transaction_bit_length

    def __init__(self, base_template, str=str):
        self.tms_string = ''.join(str(x) for x in reversed(base_template.tms))
        self.transaction_bit_length = len(self.tms_string)
        self.set_tdi_xstring(base_template.tdi)
        self.set_tdo_xstring(base_template.tdo)

    @classmethod
    def mix_me_in(cls):
        class BaseXMixin(object):
            ''' This is designed to be a mix-in class.  It assumes that
                it can simply call self() in order to transfer data
                to/from the underlying driver object.  It is used,
                e.g. by the digilent driver.
            '''
            def make_template(self, base_template):
                return cls(base_template).get_xfer_func()
            def apply_template(self, template, tdi_array):
                return template(self, tdi_array)
        return BaseXMixin
