#! /usr/bin/env python
'''
Simplistic GDB server for LEON.
'''

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from playtag.lib.userconfig import UserConfig
from playtag.gdb.transport import connection
from playtag.leon3.jtag_ahb import LeonMem
from playtag.leon3.gdbproc import CmdProcessor

config = UserConfig()
args = config.loaddefault('leongdb.cfg')
if args:
    raise SystemExit("Unsupported arguments: %s" % args)

cablemodule = config.getcable()

try:
    driver = cablemodule.Jtagger(config)
    if config.SHOW_CABLE and not config.SHOW_CONFIG:
        print "\nUsing driver %s, device %s" % (config.CABLE_DRIVER, config.CABLE_NAME)

    if not os.path.exists(config.JTAGID_FILE) and '/' not in config.JTAGID_FILE:
        config.JTAGID_FILE = os.path.join(config.root, config.JTAGID_FILE)

    if not os.path.exists(config.JTAGID_FILE):
        config.error("Cannot find LEON JTAG ID file %s" % config.JTAGID_FILE)

    processor = CmdProcessor(LeonMem(driver, config), config)
except SystemExit, s:
    if 'Configuration file settings' in str(s):
        raise
    config.error(s)
except:
    config.deferred_error()
    raise

if config.SHOW_CONFIG:
    print config.dump()

def serve_gdb():
    connection(processor, address=config.SOCKET_ADDRESS, logpackets=config.LOGPACKETS)

if __name__ == '__main__':
    serve_gdb()

