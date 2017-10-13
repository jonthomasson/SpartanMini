'''
This module provides a JtagTemplate class and a JtagTemplateFactory class.

It relies on the jtagstates module to provide it state information.

When you instantiate a JtagTemplate instance, you must pass it the
function to use for JTAG transport.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

from .states import states as jtagstates
from .. import iotemplate

TDIVariable = iotemplate.TDIVariable
defaultvar = TDIVariable()

class JtagTemplate(iotemplate.IOTemplate):
    ''' A JtagTemplate object is used to define
        a path through the JTAG state machine with
        definitions for TMS, TDI, and TDO.

        In theory, the IOTemplate base class ought to be
        usable for SPI and other things besides JTAG.
        In this class, we add JTAG-specific functions.
    '''

    # Get the jtag state vars from the states module
    vars().update(vars(jtagstates))

    def protocol_init(self, kwds):
        ''' Called by __init__.  Sets up protocol-specific instance info.
        '''
        self.states = [kwds.pop('startstate', self.unknown)]
        bypass_dict = {}
        self.bypass_info = bypass_dict.get
        bypass_info = kwds.pop('bypass_info', None)
        if bypass_info is not None:
            bypass_dict[self.shift_ir] = bypass_info.next_ir, bypass_info.prev_ir
            bypass_dict[self.shift_dr] = bypass_info.next_dr, bypass_info.prev_dr
        assert not kwds, kwds

    def protocol_copy(self, new):
        ''' Called by self.copy().  Copy our protocol
            specific stuff to new object.
        '''
        new.states = list(self.states)
        new.bypass_info = self.bypass_info
        return new

    def protocol_loop(self, prev):
        ''' To be overridden by protocol-specific subclass
        '''
        prev.states = [self.states[-1]]
        prev.bypass_info = self.bypass_info

    def protocol_add(self, other):
        ''' Called when adding two instances together.
            Makes sure they are compatible (ending state of first
            == starting state of second) and then add them together.
        '''
        states, ostates = self.states, other.states
        assert states[-1][ostates[1]] == ostates[0][ostates[1]], (
            "Mismatched state transitions on add:  %s -> %s not same TMS values as %s -> %s" %
            (states[-1], ostates[1], ostates[0], ostates[1]))
        assert self.bypass_info is other.bypass_info, (self.bypass_info, other.bypass_info)
        states.extend(ostates[1:])
        return self

    def protocol_mul(self, multiplier):
        ''' Called when multiplying an instance by an integer.
            Make sure this is legal (ending state same as startin
            state), and then do the multiply on our states.
        '''
        states = self.states
        assert states[-1][states[1]] == states[0][states[1]], (
            "Mismatched state transitions on multiply:  %s -> %s not same TMS values as %s -> %s" %
            (states[-1], states[1], states[0], states[1]))
        endstate = states.pop()
        states *= multiplier
        states.append(endstate)
        return self

    def update(self, state, tdi=defaultvar, adv=None, read=False):
        ''' update is the primary function that adds information to the
            template.  Other functions call update.
            'state' is either a number of times to remain in the current
            state or a new state to move to.
            tdi is the tdi value to use.
            adv is set True to advance out of the state (e.g. IR_SHIFT
            or DR_SHIFT) on the last clock.
            read is set true to add information to the template to capture
            TDO for the time of the update.
        '''
        self.devtemplate = None
        tmslist = self.tms
        tmslen = len(tmslist)
        states = self.states
        oldstate = states[-1]
        if isinstance(state, str) and state.isdigit() and tdi is defaultvar:
            tdi = state
            state = len(tdi)
        if isinstance(state, int):
            numbits = state
            tmslist.extend(oldstate.cyclestate(numbits))
            if adv:
                tmslist[-1] ^= 1
                states.append(oldstate[tmslist[-1]])
            if not oldstate.shifting:
                # Handle run/idle
                assert not read
                assert tdi is defaultvar
                tdi = 0
        else:
            assert adv is None, state
            newtms = oldstate[state]
            states.append(state)
            tmslist.extend(newtms)
            numbits = len(newtms)
            if tdi is defaultvar:
                tdi = numbits * '*'
            assert not read
        self.tdi.append((numbits, tdi))
        if read:
            self.tdo.append((tmslen - self.prevread, numbits))
            self.prevread = tmslen
        return self

    def readwrite(self, state, numbits, tdi, adv, read):
        prefix, suffix = self.bypass_info(state, ('', ''))
        if self.states[-1] != state:
            self.update(state)
            if prefix:
                self.update(prefix)
        self.update(numbits, tdi, adv and not suffix, read)
        if adv:
            if suffix:
                self.update(suffix, adv=True)
            self.update(self.select_dr)
        return self

    def writei(self, numbits, tdi=defaultvar, adv=True):
        ''' Write to the JTAG instruction register
        '''
        return self.readwrite(self.shift_ir, numbits, tdi, adv, False)

    def writed(self, numbits, tdi=defaultvar, adv=True):
        ''' Write to the JTAG data register
        '''
        return self.readwrite(self.shift_dr, numbits, tdi, adv, False)

    def readi(self, numbits, adv=True, tdi=0):
        ''' Read from the JTAG instruction register
        '''
        return self.readwrite(self.shift_ir, numbits, tdi, adv, True)

    def readd(self, numbits, adv=True, tdi=0):
        ''' Read from the JTAG data register.
        '''
        return self.readwrite(self.shift_dr, numbits, tdi, adv, True)
