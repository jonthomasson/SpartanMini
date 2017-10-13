#! /usr/bin/env python

'''
This module contains a parser for SVF commands.  Initial version
does not support PIOMAPs.

Copyright (C) 2013 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

import re
import zipfile
from collections import namedtuple

dotest = __name__ == '__main__'
if dotest:
    import sys
    sys.path.insert(0, '../..')

from playtag.jtag.states import states as jtagstates

class SvfError(Exception):
    pass

class ParseSVF(object):
    ''' ParseSVF is a parser class.  An instantiation of this
        has a parse() method, that can be used to iterate over
        a SVF file.  The SVF file may be stored in a zip archive
        as long as it is the only SVF file in the archive.

        The parse method returns an iterable that will iterate
        over all the records in the SVF file that require external
        action.  These records can be used as-is, and/or the class
        may be subclassed to replace the default named-tuple returned
        for each action.
    '''

    class AnyDict(dict):
        '''  Silly little generic access class
        '''
        def __init__(self):
            self.__dict__ = self

    class DataStream(object):
        ''' Keep information about TDI/TDO data or mask.
        '''
        def __init__(self, linenum=0, length=0, data=None):
            self.length = length
            self.linenum = linenum
            self.data = data or ()
        def __str__(self):
            multiple = len(self.data) > 1
            return '(length=%s data=%s%s)' % (self.length,
                     self.data and self.data[0],
                        multiple and ', ...' or '')
        def __repr__(self):
            return str(self)


    timing = dict(TCK=0, SCK=1, SEC=2)
    paramtypes = 'MASK SMASK TDI TDO'.split()
    nodata = DataStream()
    states = AnyDict()
    for (x,y) in vars(jtagstates).iteritems():
        states[''.join(reversed(x.split('_'))).upper()] = y
    del x, y
    stable = set('IRPAUSE DRPAUSE RESET IDLE'.split())
    valid_trst = dict(ON=0, OFF=1, Z=2, ABSENT=3)

    @staticmethod
    def fileiter(fname):
        '''  Iterate over a file, or a file inside a zip file.
             If inside a zip file, the zip file name must end
             in .zip, and the name of the compressed file mus
             end in .svf.  Filenames are case-insensitive.
        '''
        if not fname.lower().endswith('.zip'):
            return open(fname, 'rb')
        zipf = zipfile.ZipFile(fname, 'r')
        ilist = zipf.infolist()
        ilist = [x for x in ilist if x.filename.lower().endswith('.svf')]
        if len(ilist) != 1:
            raise SvfError("Expected single .svf file in archive; got %d" % len(ilist))
        return zipf.open(ilist[0], 'r')

    @staticmethod
    def gettokens(lines):
        '''  Split an SVF file into its constituent tokens
        '''
        re_expr = r'(//.*|\!.*|[a-zA-Z0-9.+-]+|\S)'
        split = re.compile(re_expr).split
        join = ''.join
        linenum = 0
        for line in lines:
            linenum += 1
            tokens = split(line)
            toss = tokens[::2]
            if join(toss).split():
                toss = [x.strip() for x in toss]
                toss = [x for x in toss if x]
                raise SvfError('Unexpected token %s on line %s' %
                            (repr(toss[0]), linenum))
            for token in tokens[1::2]:
                if not token.startswith(('//', '!')):
                    yield token, linenum

    @classmethod
    def getcmds(cls, tokens):
        '''  Given tokens, split an SVF file into commands
        '''
        cmd = []
        cmdlinenum = 0
        for token, linenum in tokens:
            if token not in ';(':
                cmdlinenum = cmdlinenum or linenum
                cmd.append(token.upper())
            elif token == ';':
                if not cmd:
                    continue
                yield cmd, cmdlinenum
                cmd = []
                cmdlinenum = 0
            else:
                subcmd = []
                for token, linenum in tokens:
                    if token in ');':
                        if token == ';':
                            raise SvfError(
                                'Missing ")" in command %s on line %s',
                                repr(cmd[0]), cmdlinenum)
                        cmd.append(cls.DataStream(linenum=cmdlinenum, data=subcmd))
                        break
                    subcmd.append(token)
        if cmd:
            yield cmd, cmdlinenum

    def __init__(self):
        ''' SVF files maintain state for the header, trailer
            starting and ending JTAG states, etc.  Initialize all
            this.
        '''
        sticky = self.AnyDict()
        for cmd in 'SIR SDR HIR HDR TIR TDR'.split():
            cmddict = sticky[cmd] = self.AnyDict()
            cmddict.length = 0
            for param in self.paramtypes:
                cmddict[param] = self.nodata
        self.sticky = sticky
        self.FREQUENCY = None
        idle = self.ENDDR = self.ENDIR = self.states.IDLE
        self.RUNSTATE = self.ENDSTATE = idle
        self.CURSTATE = self.states.UNKNOWN

    def cmd_enddrir(self, cmd, iterparams, linenum):
        for state in iterparams:
            if state not in self.stable:
                raise SvfError('%s is not a valid SVF stable state' % state)
            for dummy in iterparams:
                raise SvfError("Expected single state parameter")
        setattr(self, cmd, self.states[state])


    def cmd_frequency(self, cmd, iterparams, linenum):
        freq = None
        for freq in iterparams:
            try:
                freq = float(freq)
            except:
                raise SvfError('%s is not a valid floating point number' %
                    freq)
            tokcount = 0
            for hz in iterparams:
                tokcount += 1
            if tokcount != 1 or hz != 'HZ':
                raise SvfError('Unexpected text after frequency')
        self.FREQUENCY = freq
        return self.Frequency(freq, linenum)
    Frequency = namedtuple('Frequency', 'freq, linenum')

    def cmd_reg(self, cmd, iterparams, linenum):
        mydict = self.sticky[cmd]
        try:
            length = mydict.length = int(iterparams.next())
        except:
            raise SvfError('Missing or invalid bit count')
        for p in self.paramtypes:
            plen = mydict[p].length
            if plen and plen != length:
                mydict[p] = self.nodata
        for param in iterparams:
            if param not in mydict:
                raise SvfError('Unknown parameter name %s' % repr(param))
            try:
                data = iterparams.next()
            except StopIteration:
                data = ''
            if not isinstance(data, self.DataStream):
                raise SvfError("Expected (<hex data>) after parameter %s" % param)
            data.length = length
            mydict[param] = data


    def cmd_runtest(self, cmd, iterparams, linenum):
        use_sck = False
        secs = [None, None]
        numclocks = None
        do_max = do_end = did_end = False
        prev_num = None
        for param in iterparams:
            num = prev_num
            prev_num = None
            clock_specified = numclocks != secs[0]
            if num is not None:
                clocktype = self.timing.get(param)
                if clocktype is None:
                    raise SvfError('Unexpected clause "%s %s"' %
                            (num, param))
                if clocktype == 2:
                    if secs[do_max] is not None:
                        raise SvfError('%sSeconds specified twice' %
                            (do_max and 'Maximum ' or ''))
                    try:
                        secs[do_max] = float(num)
                    except:
                        raise SvfError("%s is not a valid floating point number" % num)
                else:
                    use_sck = clocktype == 1
                    if do_max or clock_specified:
                        raise SvfError('Invalid %s specification' % param)
                    try:
                        numclocks = int(num)
                    except:
                        raise SvfError("%s is not a valid integer number" % num)
            elif param in self.stable:
                if do_end and not did_end and clock_specified:
                    self.ENDSTATE = states[param]
                    did_end = True
                elif not do_end and not clock_specified:
                    self.RUNSTATE = self.ENDSTATE = states[param]
                else:
                    raise SvfError('Unexpected state %s' % param)
            elif do_end:
                raise SvfError('Invalid endstate %s' % param)
            elif param == 'MAXIMUM':
                if secs[0] is None or secs[1] is not None:
                    raise SvfError('Cannot do MAXIMUM SEC without SEC')
                do_max = True
            elif param == 'ENDSTATE':
                if not clock_specified:
                    raise SvfError('Unexpected ENDSTATE')
                do_end = True
            else:
                prev_num = param
        prevstate, self.CURSTATE = self.CURSTATE, self.ENDSTATE
        return self.RunTest(numclocks, use_sck, secs, prevstate, self.RUNSTATE, self.ENDSTATE, linenum)
    RunTest = namedtuple('RunTest', 'numclocks, use_sck, secs, prevstate, runstate, endstate, linenum')

    def cmd_shift(self, cmd, iterparams, linenum):
        self.cmd_reg(cmd, iterparams, linenum)
        assert cmd in ('SIR', 'SDR')
        which = cmd[1]
        header = 'H%sR' % which
        trailer = 'T%sR' % which
        sticky = self.sticky
        endstate = getattr(self, 'END%sR' % which)
        state = self.states[which + 'RSHIFT']
        prevstate, self.CURSTATE = self.CURSTATE, endstate
        return self.Shift(prevstate, state, endstate, sticky[header], sticky[cmd], sticky[trailer], linenum)
    Shift = namedtuple('Shift', 'prevstate, state, endstate, header, data, trailer, linenum')

    def cmd_state(self, cmd, iterparams, linenum):
        statelist = []
        getstate = self.states.get
        for state in iterparams:
            s = getstate(state)
            if s is None:
                raise SvfError('Invalid state %s' % state)
            statelist.append(s)
        if state not in self.stable:
            raise SvfError('%s is not a stable state' % state)
        prevstate, self.CURSTATE = self.CURSTATE, statelist[-1]
        return self.State(prevstate, tuple(statelist), linenum)
    State = namedtuple('State', 'prevstate, statelist, linenum')

    def cmd_trst(self, cmd, iterparams, linenum):
        try:
            param, = iterparams
        except ValueError:
            raise SvfError('Expected a single parameter')
        value = self.valid_trst[param]
        if value is None:
            raise SvfError('%s is not a valid TRST value' % param)
        if not value:
            self.CURSTATE = self.states.RESET
        return self.Trst(value, linenum)
    Trst = namedtuple('TRST', 'value, linenum')

    cmds = dict(ENDIR=cmd_enddrir, ENDDR=cmd_enddrir, FREQUENCY=cmd_frequency,
                HDR=cmd_reg, HIR=cmd_reg, TDR=cmd_reg, TIR=cmd_reg,
                SIR=cmd_shift, SDR=cmd_shift, RUNTEST=cmd_runtest,
                STATE=cmd_state, TRST=cmd_trst)

    def parse(self, fname):
        myiter = self.fileiter(fname)
        myiter = self.gettokens(myiter)
        myiter = self.getcmds(myiter)
        getproc = self.cmds.get
        try:
            for params, linenum in myiter:
                iterparams = iter(params)
                cmd = iterparams.next()
                cmdproc = getproc(cmd)
                if cmdproc is None:
                    raise SvfError('Unknown command')
                value = cmdproc(self, cmd, iterparams, linenum)
                if value is not None:
                    yield value
        except SvfError, m:
            raise SvfError("Error in line %s of file %s:\n   Command %s: %s" %
                (linenum, fname, cmd, m.message))

if dotest:
    from time import time
    starttime = time()
    fname, = sys.argv[1:]
    for stuff in ParseSVF().parse(fname):
        print stuff
        print
    print time() - starttime
