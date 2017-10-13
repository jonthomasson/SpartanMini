#!/usr/bin/env python
'''
A tool for checking our database against the urjtag database.
'''

import os
import sys
from collections import defaultdict

sys.path.append('../../')
from playtag.bsdl.lookup import PartInfo, readfile

topdir = '/usr/share/urjtag'

def checkpart(part, mfgcodes):
    y = int(part, 2) << 12
    possible = [(x << 28) + y + z for x in range(16) for z in mfgcodes]
    possible = [PartInfo(x) for x in possible]
    actual = [x for x in possible if x.ir_capture]
    print actual and actual[0] or possible[0]
    return bool(actual)

def do_mfg():
    total = 0
    matched = 0
    by_mfg = defaultdict(list)
    unmatched = []

    for line in readfile(os.path.join(topdir, 'MANUFACTURERS')):
        index, name = list(line)[:2]
        by_mfg[name].append((int(index,2) << 1) + 1)

    for name, items in sorted(by_mfg.iteritems()):
        print
        print name, items
        subdir = os.path.join(topdir, name)
        partfile = os.path.join(subdir, 'PARTS')
        if not os.path.exists(partfile):
            print "No parts"
            continue
        parts = (list(x) for x in readfile(partfile))
        parts = list((x[0], ' '.join(x[2:])) for x in parts)
        if not parts:
            print "No parts (2)"
            continue

        for partnum, partname in parts:
            found = checkpart(partnum, items)
            matched += found
            if not found:
                unmatched.append('    %s %s %s' % (name, partname, partnum))
        total += len(parts)
    print "Total parts = %s; %s matched, %s missing" % (total, matched, total-matched)
    for stuff in unmatched:
        print stuff
do_mfg()
