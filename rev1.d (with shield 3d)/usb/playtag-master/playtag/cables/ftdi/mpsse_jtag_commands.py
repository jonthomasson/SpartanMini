'''
This module contains code to map JTAG TMS/TDI/TDO template strings into
FTDI MPSSE commands.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''
import re
import itertools

from .mpsse_commands import Commands, hexconv


debug = True

if debug:
    def printbytes(s):
        column = 0
        for x in (s[i:i+8] for i in range(0, len(s), 8)):
            try:
                x = hex(int(x, 2))
            except:
                pass
            print x,
            column += len(x) + 1
            if column > 120:
                print '...'
                column = 0
        print

def group_strings(tms, tdi, tdo, slice=slice, len=len):
    ''' NOTE: Strings are reversed -- s[0] is later in time than s[30]
    '''
    def key(stuff):
        tms, tdi, tdo = stuff
        if tms != '0' or tdi == tdo == '*':
            return 'tms' + tdi
        elif tdi == 'x' or tdo == 'x':
            return 'data'
        else:
            return 'null'

    def null2data(data):
        ''' Convert big blocks of null into null followed by data.
            (strings are reversed, so emit data first.)
        '''
        for item in data:
            if item[0] == 'null' and len(item[1]) >= 17:
                yield ['data', item[1][:-8]]
                item[1] = item[1][-8:]
            yield item

    def mergenull(data):
        ''' Coalesce data/null together
        '''
        later = data.next()
        for item in data:
            if item[0] == 'data' and later[0] == 'null':
                later[1] += item[1]
                later[0] = 'data'
                continue
            yield later
            later = item
        yield later

    def optimizedata(data):
        ''' Coalesce data/data together, and move data from
            preceding null to align to byte boundaries if possible
        '''
        later = data.next()
        for item in data:
            if later[0] == 'data':
                if item[0] == 'data':
                    later[1] += item[1]
                    continue
                if item[0] == 'null':
                    even = -len(later[1]) % 8 + ((len(item[1]) - 1) // 8 * 8)
                    if even < len(item[1]):
                        later[1] += item[1][:even]
                        item[1] = item[1][even:]
            yield later
            later = item
        yield later

    def get_transitions(data):
        start = 0
        for item in data:
            yield start
            start += len(item[1])
        yield start

    join = ''.join
    data = ([x,join(z[1] for z in y)] for (x,y) in itertools.groupby(itertools.izip(tms, tdi, tdo), key))
    data = null2data(data)
    data = mergenull(data)
    data = optimizedata(data)
    startx, stopx = itertools.tee(get_transitions(data))
    stopx.next()
    slices = (slice(x, y) for (x, y) in itertools.izip(startx, stopx))
    return [(tms[x], tdi[x], tdo[x]) for x in slices]

def do_tdi_tdo(info, addwrite, addread, old_tdi):
    tms, tdi, tdo = info.pop()
    length = len(tdi)
    assert tms.count('0') == length == len(tdo)
    bytes, bits = divmod(length, 8)
    leftovers = -bits % 8 * '0'
    if 'x' not in tdo:
        instructions = Commands.tdi_wr, Commands.tdi_wr_bits
    else:
        addread(tdo[bits:])
        addread(leftovers)
        addread(tdo[:bits])
        if old_tdi == '0' and tdi.count('0') == len(tdi):
            instructions = Commands.tdo_rd, Commands.tdo_rd_bits
            tdi = leftovers = ''
        else:
            instructions = Commands.tdi_tdo, Commands.tdi_tdo_bits
    if bytes:
        if bytes == 1:
            addwrite(hexconv(instructions[1]))
            addwrite(hexconv(8-1))
        else:
            addwrite(hexconv(instructions[0]))
            addwrite(hexconv( (bytes-1) % 256))
            addwrite(hexconv( (bytes-1) / 256))
        addwrite(tdi[bits:])
    if bits:
        addwrite(hexconv(instructions[1]))
        addwrite(hexconv(bits-1))
        addwrite(tdi[:bits])
        addwrite(leftovers)
    return '0', tdi and tdi[0] or '0'   # TMS

def do_tms(info, addwrite, addread, old_tdi):
    maxbits = room = 7
    tms, tdi, tdo = [], [], []
    tdival = info[-1][1][-1]
    while info and room:
        new_tms, new_tdi, new_tdo = info[-1]
        if new_tms == '1' and new_tdi == 'x':
            if not tms:
                info.pop()
                tms.append(new_tms); tdi.append(new_tdi); tdo.append(new_tdo)
            break
        if (new_tms[-1] == '0' and (new_tdi[-1] != '*' or len(new_tdi) >= 16)) and tms:
            break
        mylen = min(room, len(new_tms))
        bad_tdi = new_tdi[-mylen:].upper()  # Force mismatch on 'X'
        if not tdi and bad_tdi.endswith('X'):
            bad_tdi = bad_tdi[:-1]
        while 1:
            bad_tdi = bad_tdi.rstrip(tdival+'*')
            if not bad_tdi or tdival != '*':
                break
            tdival = bad_tdi[-1]
        mylen -= len(bad_tdi)
        if not mylen:
            break
        info.pop()
        room -= mylen
        if mylen < len(new_tdi):
            room = 0
            info.append((new_tms[:-mylen], new_tdi[:-mylen], new_tdo[:-mylen]))
            new_tms, new_tdi, new_tdo = new_tms[-mylen:], new_tdi[-mylen:], new_tdo[-mylen:]
        tms.append(new_tms); tdi.append(new_tdi); tdo.append(new_tdo)

    tdival = tdival.replace('*', '0')
    tms.reverse()
    tdi.reverse()
    tdo.reverse()
    tms = ''.join(tms)
    tdi, = set(''.join(tdi).replace('*', tdival))  # Check it doesn't change
    tdo = ''.join(tdo)
    length = len(tms)
    assert 1 <= length <= maxbits
    assert length == 1 or tdi != 'x'
    if 'x' not in tdo:
        instruction = Commands.tms_wr_bits
    else:
        instruction = Commands.tms_rd_bits
        addread((8-length) * '0')
        addread(tdo)
    addwrite(hexconv(instruction))
    addwrite(hexconv(length-1))
    addwrite(tms)
    addwrite((7 - length) * '0')
    addwrite(tdi)
    return tms[0], tdi

def mpsse_jtag_commands(tms, tdi, tdo, do_tms=do_tms, do_tdi_tdo=do_tdi_tdo):
        def get_func():
            new_tms, new_tdi, new_tdo = info[-1]
            if new_tms[-1] == old_tms == '0':
                if len(new_tms) >= 7:
                    return do_tdi_tdo
                if len(set(new_tdi.replace('*', ''))) > 1:
                    return do_tdi_tdo
                if new_tdi.count('x') > 1:
                    return do_tdi_tdo
            return do_tms

        info = group_strings(tms, tdi, tdo)
        write_template, read_template = [], []
        addwrite, addread = write_template.append, read_template.append
        old_tms = '0'
        old_tdi = '*'
        while info:
            old_tms, old_tdi = get_func()(info, addwrite, addread, old_tdi)

        write_template.reverse()
        read_template.reverse()
        return ''.join(write_template), ''.join(read_template)
