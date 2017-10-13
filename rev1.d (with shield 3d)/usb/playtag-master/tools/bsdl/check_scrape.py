#!/usr/bin/env python
'''
CHeck that the scraped files are contiguous.
'''

import os

nums = set()
for fname in os.listdir('downloads'):
    x = fname.split('=', 1)
    if x[0] == 'download.htm?id' and x[-1].isdigit():
        nums.add(int(x[-1]))
    else:
        print "Unknown file", fname

missing = set(range(min(nums), max(nums) + 1)) - nums
if not missing:
    print "All present and accounted for"
else:
    print "Missing", missing
