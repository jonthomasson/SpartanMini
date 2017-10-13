#! /usr/bin/env python
'''
Simplistic chain discovery
'''

import sys
import os

os_cmd = sys.argv[0]

root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, root)

from playtag.lib.userconfig import UserConfig
from playtag.jtag.discover import Chain

config = UserConfig()
config.readargs(parseargs=True)

def showtypes():
    cables = os.listdir(os.path.join(root, 'playtag/cables/'))
    cables = (x for x in cables if not x.startswith(('_', '.')))
    raise SystemExit('''

usage: %s <cabletype> [<cablename>] [<option>=<value>]

Valid cabletypes are the subpackages under playtag/cables:
    %s

Valid cablenames and options vary by cabletype --
    type '%s <cabletype>' for a list.

You can either give the name of the cable, or the index number.
For example if you have a single digilent USB cable, you could
type either:

    %s digilent DCabUsb

or:

    %s digilent 0

''' % (os_cmd, ', '.join(sorted(cables)), os_cmd, os_cmd, os_cmd))

if config.CABLE_DRIVER is None:
    showtypes()

cablemodule = config.getcable()

if config.CABLE_NAME is None:
    cablemodule.showdevs()
    raise SystemExit

driver = cablemodule.Jtagger(config)

ismain = __name__ == '__main__'

if ismain and config.SHOW_CONFIG:
    print config.dump()

chain = Chain(driver)

if ismain:
    print chain
