#! /usr/bin/env python

import time
from leonserver import config, processor


print processor.monitor_load(config.LOAD_FILE)
print processor.monitor_verify(config.LOAD_FILE)

try:
    while 1:
        poll = processor.cpu_pollstop()
        print "Running...  (ctrl-C to stop)"
        while not poll():
            time.sleep(0.3)
except KeyboardInterrupt:
    print "\nStopping..."
    processor.monitor_reset('-q')
