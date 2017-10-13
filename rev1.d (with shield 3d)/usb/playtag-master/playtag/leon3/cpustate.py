'''
This cpustate module uses an object that can read/write the AHB
(such as instantiated from jtag_ahb) along with knowledge of DSU
registers (from dsuregs.py) to determine the configuration and state
of the LEON3 core.

Does not yet know about plug and play information.  Requires external
assistance to tell it where the DSU is.  Should add reset randomization
capability.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

from math import log
from . import dsuregs
from ..lib.abstractreg import HexNum

class ASICodes(object):
    IRAM = 0x9 # Local instruction RAM
    DRAM = 0xB # Local data RAM
    ICACHE_TAGS = 0xC # Instruction cache tags
    ICACHE_DATA = 0xD # Instruction cache data
    DCACHE_TAGS = 0xE # Data cache tags
    DCACHE_DATA = 0xF # Data cache data
    SNOOP_TAGS = 0x1E # Separate snoop tags
    RAM = IRAM, DRAM
    CTAGS = ICACHE_TAGS, DCACHE_TAGS, SNOOP_TAGS
    CDATA = ICACHE_DATA, DCACHE_DATA

class CacheInfo(object):
    def __init__(self, cfg, cachetype):
        self.cachetype = cachetype
        self.can_lock = bool(cfg.CL)
        self.replacement = 'direct LRU LRR random'.split()[cfg.REPL]
        self.can_snoop = bool(cfg.SN)
        self.ways = 1 + cfg.SETS
        self.way_size = HexNum(1024 << cfg.SSIZE)
        self.cache_size = self.ways * self.way_size
        self.ram_size = cfg.LR and HexNum(1024 << cfg.LRSIZE)
        self.ram_addr = cfg.LR and HexNum(cfg.LRSTART << 24)
        self.line_size = HexNum(4 << cfg.LSIZE)
        self.has_mmu = bool(cfg.M)

        self.waysel_bits = int(round(log(self.ways + (self.ways==3)) / log(2)))
        self.line_bits   = int(round(log(self.line_size) / log(2)))
        self.way_bits    = int(round(log(self.way_size) / log(2))) - self.line_bits


    def __repr__(self):
        cachetype = 'Instruction Data'.split()[self.cachetype]
        result = ['%-12s = %s' % x for x in sorted(vars(self).iteritems())]
        return '%s cache:\n    ' % cachetype + '\n    '.join(result)
    def __str__(self):
        return repr(self)


class LeonCfg(object):
    def __init__(self, ahb, user):
        self.ahb = ahb
        enable = user.DSU_ENABLE_ADDR
        if enable:
            ahb.write(enable, user.DSU_ENABLE_DATA)
        self.DSU_ADDR = HexNum(user.DSU_ADDR)
        self.AHB_RAM_ADDR = HexNum(user.AHB_RAM_ADDR)
        self.AHB_RAM_SIZE = HexNum(user.AHB_RAM_SIZE)
        self.dsu = dsu = dsuregs.DSU(user.DSU_ADDR, ahb)
        self.ctl = ctl = dsu.Control
        self.brk = brk = dsu.Break
        self.asi2 = dsu.ASI2
        self.asiram = dsu.ASIRAM
        self.reset(firsttime=True)

        self.calcram()

        stackloc = getattr(user, 'STACKLOC', None)
        if not stackloc:
            stackloc = self.dcfg.ram_addr + self.dcfg.ram_size
        if not stackloc:
            stackloc = self.AHB_RAM_ADDR + self.AHB_RAM_SIZE
        self.STACKLOC = stackloc - 4

    def calcram(self):
        cfgs = [x for x in (self.dcfg, self.icfg) if x.ram_size]
        blocksize = cfgs and min(x.ram_size for x in cfgs) or 2
        blocks = {}
        asiram = self.asiram.baseaddr
        for cfg in cfgs:
            asicode = ASICodes.RAM[cfg.cachetype]
            for offset in range(0, cfg.ram_size, blocksize):
                blocks[HexNum(cfg.ram_addr + offset)] = HexNum(asicode), HexNum(asiram + offset)
        self.ram_blocks = blocks
        self.ram_mask = HexNum((1 << 32) - blocksize)

    def reset(self, firsttime=False):
        ### TODO: Add randomize, full stuff
        dsu = self.dsu
        ctl = self.ctl
        brk = self.brk
        ctl.HL = 1
        ctl.BW = 1
        brk.BN0 = 1
        ctl.store()
        brk.store().load()
        ctl.load()
        assert ctl.HL and ctl.EE and ctl.DM

        dsu.IUREG[:] = len(dsu.IUREG) * [0]
        dsu.SPECIALREG[:] = len(dsu.SPECIALREG) * [0]

        dsu.PC.store(self.AHB_RAM_ADDR)
        dsu.NPC.store(self.AHB_RAM_ADDR + 4)
        psr = dsu.PSR
        psr.S = 1
        psr.ET = 0
        psr.store()
        self.asireg = asi = dsu.ASI
        asi.store(2)
        asi2 = self.asi2
        asi2.CCR.store(0)  # Clear cache bits

        asr17 = dsu.ASR17.store().load()
        if firsttime:
            self.NUM_WINDOWS = asr17.NWIN + 1
            self.NUM_WATCHPOINTS = asr17.NWP
            self.icfg = CacheInfo(asi2.ICFG.load(), 0)
            self.dcfg = CacheInfo(asi2.DCFG.load(), 1)

    def clearcache(self):
        # TODO:  Use a scalpel, not a sledgehammer
        size = self.icfg.cache_size / 4
        self.asireg.store(ASICodes.ICACHE_TAGS)
        self.asiram[:size] = size * [0]
        size = self.dcfg.cache_size / 4
        self.asireg.store(ASICodes.DCACHE_TAGS)
        self.asiram[:size] = size * [0]

    def flushcache(self):
        asi = self.asireg
        saveasi = asi.load().value
        asi.store(2)
        CCR = self.asi2.CCR
        CCR.load()
        CCR.FD = CCR.FI = 1  # Flush the caches
        CCR.store()
        asi.store(saveasi)

    def remap_addr(self, addr):
        topbits = addr & self.ram_mask
        remap = self.ram_blocks.get(topbits)
        if not remap:
            return addr
        asival, newtop = remap
        self.asireg.store(asival)
        return addr - topbits + newtop

    def __repr__(self):
        result = ['%-12s = %s' % x for x in sorted(vars(self).iteritems())]
        return '\n'.join(result)
    def __str__(self):
        return repr(self)
