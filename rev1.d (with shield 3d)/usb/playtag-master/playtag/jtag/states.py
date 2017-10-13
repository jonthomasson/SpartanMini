#! /usr/bin/env python
'''
Develop a JTAG state transition graph that shows TMS values for
transitions from any state to any other state.

This module knows a lot about the JTAG state machine, but
in a completely implementation independent way.

Examples:

  jtagstates.states.reset.shift_dr  returns the TMS sequence to get from reset to shift_dr
  jtagstates.states.unknown.shift_dr returns the TMS sequence to get from any state to shift_dr
  jtagstates.states.reset[0] returns the idle state (reset + TMS value of 1)

  jtagstates.states.reset.cyclestate(2) returns [1,1] as the TMS value that is required to
  keep the state machine in that state for two cycles.

A TMS path that is returned may be modified by calling its pad method to define a minimum length
or a boundary condition for the number of bits modulo some number.

Run this module standalone for a list of state names and sequence values.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

from collections import defaultdict

#   Start       TMS=0       TMS=1
transitions = '''
    reset       idle        reset
    idle        idle        select_dr
    select_dr   capture_dr  select_ir
    capture_dr  shift_dr    exit1_dr
    shift_dr    shift_dr    exit1_dr
    exit1_dr    pause_dr    update_dr
    pause_dr    pause_dr    exit2_dr
    exit2_dr    shift_dr    update_dr
    update_dr   idle        select_dr
    select_ir   capture_ir  reset
    capture_ir  shift_ir    exit1_ir
    shift_ir    shift_ir    exit1_ir
    exit1_ir    pause_ir    update_ir
    pause_ir    pause_ir    exit2_ir
    exit2_ir    shift_ir    update_ir
    update_ir   idle        select_dr
'''

class states(object):
    pass
states = states()

class OneState(str):
    ''' For each state, maintain a dictionary:
          Dictionary keys = other states
          Dictionary values = TMS sequences to transition to the other states
    '''
    order = []
    def __new__(cls, name, cache={}):
        name = str(name)
        try:
            return cache[name]
        except KeyError:
            pass
        cache[name] = self = str.__new__(cls, name)
        self.shifting = name.startswith('shift')
        self.sequences = {}
        setattr(states, self, self)
        self.order.append(self)
        return self

    def __getitem__(self, index):
        if isinstance(index, str):
            return TMSPath(self, index)
        return transitions[self][index]

    def __getattr__(self, name):
        return TMSPath(self, name)

    def cyclestate(self, count=1):
        for value in range(2):
            if self[value] == self:
                return count * [value]
        raise ValueError("%s is not a valid cycle state" % self)


class TMSPath(list):
    ''' Define a list of TMS transitions required to get from one state to another.
        Optionally pad to a given required length.
    '''
    def __init__(self, startstate, endstate):
        self[:] = startstate.sequences[endstate]
        self.startstate = startstate
        self.endstate = endstate

    def pad(self, minlen=1, stride=1, offset=0, minpause=0, pausestate=None):
        ''' Pad the length of the sequence by pausing on an intermediate state
            for awhile.  Flexible padding can specify:
              - State to pause on
              - Minimum number of cycles to spend in paused state:
                    - 0 means not required to go through paused state
                    - 1 means required to go through paused state
                    - 2 means required to be in paused state at least 2 cycles
                    - etc.
              - Minimum number of states in the entire path from start to end state
              - Number of states must be 'offset' modulo 'stride'
        '''
        assert 0 <= offset < stride, (stride, offset)
        if len(self) % stride == offset and len(self) >= minlen and not minpause:
            return self
        startstate = self.startstate
        endstate = self.endstate
        if pausestate is None:
            pausestate = states.idle
        seq1 = startstate.sequences[pausestate]
        seq2 = pausestate.sequences[endstate]
        startlen = len(seq1) + len(seq2)
        padlen = max(minpause-1, minlen - startlen, 0)
        padlen = (offset - startlen - padlen) % stride + padlen
        self[:] = seq1 + pausestate.cyclestate(padlen) + seq2
        return self

def calcpaths():
    ''' Determine minimal transitions from every state to every state.

        Algorithm:
            1) Create a set of undone source/dest states, and keep
               it updated in order to determine when we are finished,
               and also so that we don't overwrite a minimal transition
               with a longer one.

            2) Create and keep a dictionary of all transitions of length 1.
               Then, for n=2 to infinity (or until we run out of undone
               transitions), make new dictionaries for new lengths.  We don't
               add any transition to the list if a shorter transition
               for those two states already exists.
    '''
    undone = set((x,y) for x in transitions for y in transitions)
    sequences = dict((x, x.sequences) for x in transitions)

    # Create initial set of transitions of length 1
    dict0 = {}
    for start, x in transitions.iteritems():
        dict0[start] = subdict = {}
        for i, end in enumerate(x):
            undone.remove((start, end))
            sequences[start][end] = subdict[end] = [i]

    # Keep bumping up the number of transitions in the dictionary
    # until we've covered all possible transitions.
    dictn = dict0
    while undone:
        dictm = {}
        for start, subdict in dictn.iteritems():
            newdict = {}
            for mid, firstseq in subdict.iteritems():
                for end, lastseq in dict0[mid].iteritems():
                    path = start, end
                    if path in undone:
                        undone.remove(path)
                        sequences[start][end] = newdict[end] = firstseq + lastseq
            if newdict:
                dictm[start] = newdict
        assert dictm
        dictn = dictm

def checkpaths():
    ''' 1) Determine the reset sequence that will reset from any state
        2) Insure that it actually works
        3) Determine the path to get from 'unknown' state through reset to
           any desired state.
    '''
    resetseq = max(x.sequences[states.reset] for x in transitions)
    for start in transitions:
        state = start
        for index in resetseq:
            state = state[index]
        assert state is states.reset, (start, state)
    sequences = states.unknown.sequences
    sequences[states.reset] = resetseq
    for state in transitions:
        if state not in (states.unknown, states.reset):
            sequences[state] = resetseq + states.reset[state]

OneState('unknown')
# Convert the transitions into something usable
transitions = (x for x in transitions.splitlines() if x.strip())
transitions = ((OneState(y) for y in x.split()) for x in transitions)
transitions = dict((a, (b, c)) for (a, b, c) in transitions)
# Calculate the minimum paths between states, and then the reset value and paths
calcpaths()
checkpaths()

if __name__ == '__main__':
    for state1 in OneState.order:
        print
        for state2 in OneState.order[1:]:
            print '%-10s -> %-10s: %s' % (state1, state2, ''.join(str(x) for x in state1[state2]))

    x = states.unknown.shift_dr
    x.pad(stride=16)
    print x
