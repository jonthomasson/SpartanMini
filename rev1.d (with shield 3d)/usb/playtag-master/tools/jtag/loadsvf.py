#! /usr/bin/env python
from discover import driver, config
from playtag.svf import runsvf

class SvfDefaults(object):
    SVF = None

config.add_defaults(SvfDefaults)

if not config.SVF:
    print 'Expected SVF=<fname>'

runsvf(config.SVF, driver)
