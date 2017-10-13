#!/usr/bin/env python

# REQUIRES both rst2pdf and wikir project from google code.

import sys
import subprocess
sys.path.insert(0, '../../rson/py2x')
from rson import loads
from simplejson import dumps

subprocess.call('../../rst2pdf/bin/rst2pdf manual.txt -e preprocess -e dotted_toc -o manual.pdf'.split())

lines = iter(open('manual.txt', 'rb').read().splitlines())

badstuff = 'page:: space:: footer:: ##Page## contents::'.split()
result = []
for line in lines:
    for check in badstuff:
        if check in line:
            break
    else:
        result.append(line)

result.append('')
result = '\n'.join(result)

from wikir import publish_string
result = publish_string(result)

f = open('manual.wiki', 'wb')
f.write(result)
f.close()
