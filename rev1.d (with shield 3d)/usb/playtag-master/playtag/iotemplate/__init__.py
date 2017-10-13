'''
This package provides generic "IO templates."

There are two kinds of IO templates:

   Cable-independent IO templates are built using higher-level JTAG or SPI code.
   They are then transformed into cable-specific IO templates.

This init file contains the base class for the cable independent IO template.

This base class is subclassed, e.g. by jtag.tamplate.JtagTemplate to make
an IO template that has knowledge of JTAG but is still cable-independent.
Each template is then converted into cable-specific templates by the
cable driver the first time it is used.

The package directory can contain useful pieces for building cable-specific
templates, but there are no real rules on where that code goes -- if a cable
is so weird that its functions won't be useful for any other cable, that code
could go in the cable-specific directory.

Currently, the file 'stringconvert.py' resides in this directory.  It can
handle the current template conversion for digilent cables, and handles a
lot of the template conversion for FTDI cables.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

class TDIVariable(object):
    ''' TDIVariable is a place-holder for TDI bits that are supplied
        later (allowing us to make reusable templates).

        The index is used to determine which data stream to use
        to supply the variable data.  It defaults to stream 0.

        For example, the LEON client's jtag_ahb module uses
        stream 0 for processor addresses and stream 1 for processor
        data.  The actual streams are passed as parameters to the
        __call__ function of an IOTemplate instance.
    '''
    def __init__(self, index=0):
        self.index = index

class IOTemplate(object):
    ''' The default template uses JTAG-specific identifiers for internal
        variables.  Should still work for SPI, although I haven't yet
        worked out the MSB/LSB logic.

        This class is subclassed by the JtagTemplate class to add
        protocol-specific attributes and methods.

        Variable attributes:

            tms -- A list of integer 1 and 0 values, one per clock
            tdi -- A list of two different kinds of items:
                     - strings of ones and zeros
                          - output to the device rightmost character first
                     - an integer number of bits to send
            tdo -- a list of two-item tuples:
                     - Start offset in bits from previous tuple start
                     - number of bits to retrieve
            prevread -- starting position of last tuple in tdo list
            devtemplate -- Device-specific template
            loopstack -- used for building up a template by looping
                         back using loop() and endloop()

        Note:  tdo entries are maintained with offsets from previous
               entries to make it easier to splice templates together.
    '''
    prevread = 0          # Location of previous read
    devtemplate = None    # Translated device-specific template
                          # Clear this when modifying the object

    loopstack = None      # Nothing on the loop stack to start with

    def __init__(self, cable=None, cmdname='', **kwds):
        ''' Initialize all our data.  cmdname is just for debugging.
           kwds is for protocol-specific information.
        '''
        self.cable=cable
        self.cmdname = cmdname
        self.tms = []
        self.tdi = []
        self.tdo = []
        self.protocol_init(kwds)
    def protocol_init(self, kwds):
        ''' To be overridden by protocol-specific subclass
        '''
        pass

    def __len__(self):
        return len(self.tms)

    def copy(self):
        ''' Make a copy of the instance.
        '''
        new = type(self)(self.cable, self.cmdname)
        new.tms = list(self.tms)
        new.tdi = list(self.tdi)
        new.tdo = list(self.tdo)
        new.prevread = self.prevread
        new.loopstack = self.loopstack
        return self.protocol_copy(new)
    def protocol_copy(self, new):
        ''' To be overridden by protocol-specific subclass
        '''
        return new

    def loop(self):
        ''' loop/endloop pairs mark a section of the template
            that is to be repeated a fixed number of times.
            The endloop is passed the repeat count.  Zero is
            allowed.

            Push all our state onto the stack.  Do this
            by creating a 'prev' object and then stuffing
            our dict into the prev object.
        '''
        self.devtemplate = None
        prev = type(self)(self.cable)
        self.protocol_loop(prev)
        prev.__dict__, self.__dict__ = self.__dict__, prev.__dict__
        self.loopstack = prev
        return self
    def protocol_loop(self, prev):
        ''' To be overridden by protocol-specific subclass
        '''
        pass

    def endloop(self, count):
        ''' loop/endloop pairs mark a section of the template
            that is to be repeated a fixed number of times.
            The endloop is passed the repeat count.  Zero is
            allowed.

            Restore our state from a combination of our
            current state (from inside the loop) and the
            state on most recent object on the loopstack.
            Loops can be nested.
        '''
        prev, self.loopstack = self.loopstack, None
        assert type(prev) is type(self)
        self.__dict__ = (prev + count * self).__dict__
        return self

    def __add__(self, other):
        ''' Add two template objects together to form
            a new object.  Optimize addition of constant
            tdi strings.  This is used by the loop/endloop
            construct.
        '''
        self = self.copy()
        tms, tdi, tdo = self.tms, self.tdi, self.tdo
        otms, otdi, otdo = other.tms, other.tdi, other.tdo
        if not otms:
            return self
        if tdi and otdi and isinstance(tdi[-1], str) and isinstance(otdi[0], str):
            tdi[-1] = otdi[0] + tdi[-1]
            otdi = otdi[1:]
        tdi += otdi
        if otdo:
            otdo = list(otdo)
            tdoofs, tdolen = otdo[0]
            tdoofs += len(tms) - self.prevread
            otdo[0] = tdoofs, tdolen
            tdo += otdo
            self.prevread = len(tms) + other.prevread
        tms += otms
        return self.protocol_add(other)
    def protocol_add(self, other):
        ''' To be overridden by protocol-specific subclass
        '''
        return self

    def __mul__(self, multiplier):
        ''' Return a new instance that is the current instance
            multiplied by a constant.

            This is used by the loop/endloop construct.
        '''
        assert multiplier >= 0 and int(multiplier) == multiplier, multiplier
        if multiplier == 0:
            return type(self)(self.cable)
        self = self.copy()
        tms, tdi, tdo = self.tms, self.tdi, self.tdo
        if multiplier == 1:
            return self
        if tdi and isinstance(tdi[-1], str) and isinstance(tdi[0], str):
            tdilast = tdi.pop()
            if tdi:
                tdi2 = list(tdi)
                tdi2[0] = tdi2[0] + tdilast
                tdi += (multiplier-1) * tdi2
            else:
                tdilast *= multiplier
            tdi.append(tdilast)
        else:
            tdi *= multiplier
        if tdo:
            tdo2 = list(tdo)
            tdoofs, tdolen = tdo2[0]
            tdoofs += len(tms) - self.prevread
            tdo2[0] = tdoofs, tdolen
            tdo += (multiplier-1) * tdo2
            self.prevread += (multiplier-1) * len(tms)
        tms *= multiplier
        return self.protocol_mul(multiplier)
    def protocol_mul(self, multiplier):
        ''' To be overridden by protocol-specific subclass
        '''
        return self

    # As with strings, addition is not commmutative, but multiplication is.
    __rmul__ = __mul__

    def __call__(self, *tdi):
        ''' Calling the object will pass the template to the underlying
            cable driver object.  We ask the cable driver to make a
            cable-specific version of the template, which we then cache.
            On subsequent calls we only have to apply the template.

            The function is passed a list of tdi elements to apply
            the template to, and if the template had any tdo elements
            in it, the function will return an iterable for the tdo
            data.
        '''
        devtemplate = self.devtemplate
        if devtemplate is None:
            devtemplate = self.devtemplate = self.cable.make_template(self)
            self.apply_template = self.cable.apply_template
        return self.apply_template(devtemplate, tdi)
