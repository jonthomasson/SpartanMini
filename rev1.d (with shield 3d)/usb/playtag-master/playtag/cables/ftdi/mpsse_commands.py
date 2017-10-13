'''
This module contains definitions for FTDI MPSSE commands.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
import re

def hexconv(what, format = '{0:08b}'.format):
    what = format(what)
    assert len(what) == 8
    return what

class HexByte(int):
    def __or__(self, other):
        return HexByte(int(self) | int(other))
    __ror__ = __or__
    def __str__(self):
        return '0x%02x' % self
    __repr__ = __str__

class Commands(object):
    data_info = 'negedge_wr bitmode negedge_rd lsb_first tdi_wr tdo_rd tms_wr'
    vars().update(('_' + y, HexByte(1 << x)) for (x, y) in enumerate(data_info.split()))
    del data_info

    tdi_wr = _tdi_wr | _negedge_wr | _lsb_first
    tdo_rd = _tdo_rd | _lsb_first
    tdi_tdo = tdi_wr | tdo_rd

    tdi_wr_bits = tdi_wr | _bitmode
    tdo_rd_bits = tdo_rd | _bitmode
    tdi_tdo_bits = tdi_wr_bits | tdo_rd_bits
    tms_wr_bits = _tms_wr | _lsb_first | _bitmode | _negedge_wr
    tms_rd_bits = tms_wr_bits | tdo_rd_bits

    wr_gpio = tuple(HexByte(0x80 | x) for x in range(0,4,2))
    rd_gpio = tuple(1 | x for x in wr_gpio)

    loopback_en = HexByte(0x84)
    loopback_dis = loopback_en | 1

    set_divisor = HexByte(0x86)
    send_immediate = HexByte(0x87)

    disable_clk_div5 = HexByte(0x8a)
    enable_clk_div5 = HexByte(0x8b)
    disable_three_phase = HexByte(0x8d)
    disable_adaptive_clocking = HexByte(0x97)

if __name__ == '__main__':
    print [(x, getattr(Commands, x)) for x in dir(Commands) if not x.startswith('_')]
