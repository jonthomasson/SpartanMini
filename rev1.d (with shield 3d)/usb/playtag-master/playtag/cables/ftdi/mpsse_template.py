'''
This module contains a mixin object to map JTAG strings into
FTDI MPSSE commands.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
from .mpsse_jtag_commands import mpsse_jtag_commands
from ...iotemplate.stringconvert import TemplateStrings

class MpsseTemplate(TemplateStrings):

    def get_xfer_func(self):
        info = mpsse_jtag_commands(self.tms_string, self.tdi_xstring, self.tdo_xstring)
        self.tdi_xstring, self.tdo_xstring = info
        tditostr = self.get_tdi_combiner()
        tdo_length = len(self.tdo_xstring)
        tdi_length = len(self.tdi_xstring)

        if self.tdo_bits:
            tdofromstr = self.get_tdo_extractor()
            def func(driver, tdi_array):
                tdostr = driver(tditostr(tdi_array), tdi_length, tdo_length)
                return tdofromstr(tdostr)
        else:
            def func(driver, tdi_array):
                driver(tditostr(tdi_array), tdi_length, tdo_length)
        vars(self).clear()
        return func
