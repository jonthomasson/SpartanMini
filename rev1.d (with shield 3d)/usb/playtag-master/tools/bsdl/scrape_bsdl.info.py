#!/usr/bin/env python
'''
Scrape BSDL files from the web.

Currently only knows about bsdl.info, and has hard-coded limits...
'''
import os
import subprocess
import random

os.chdir('downloads')
existing = os.listdir('.')
existing = [x.split('=')[-1] for x in existing]
existing = [int(x) for x in existing if x.isdigit]

filenums = list(set(range(1,7128)) - set(existing))

for i in range(100):
    random.shuffle(filenums)

prefix = '/usr/bin/wget -nv --limit-rate=500k'.split()
while filenums:
    shortlist = filenums[-8:]
    del filenums[-8:]
    shortlist = ['www.bsdl.info/download.htm?id=%d' % x for x in shortlist]
    result = subprocess.call(prefix + shortlist)
    print result, len(filenums)
