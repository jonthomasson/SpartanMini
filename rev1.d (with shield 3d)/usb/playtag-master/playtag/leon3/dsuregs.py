'''
Define the structure of registers in the LEON3 DSU.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

from ..lib.abstractreg import Block, BlockArray, Register

class DSU(Block):
    size = 0x800000

    class Control(Register):
        offset = 0
        TE = 0
        BE = 1
        BW = 2
        BS = 3
        BX = 4
        BZ = 5
        DM = 6
        EE = 7
        EB = 8
        PE = 9
        HL = 10
        PW = 11

    class Timer(Register):
        offset=8

    class Break(Register):
        offset = 0x20
        BN0 = 0
        SS0 = 16

    class DebugModeMask(Register):
        offset = 0x24

    class IUREG(Block):
        offset = 0x300000
        size = 0x800

    class SPECIALREG(Block):
        offset = 0x400000
        size = 0x80

    class Y(Register):
        offset = 0x400000

    class PSR(Register):
        offset = 0x400004
        IMPL = 31, 28       # Implementation-specific codes
        VER = 27, 24        # Version info
        ICC = 23, 20        # Integer condition codes
        EC = 13             # Enable coprocessor
        EF = 12             # Enable floating point
        PIL = 11, 8         # Processor interrupt level
        S = 7               # Supervisor mode
        PS = 6              # Previous supervisor mode
        ET = 5              # Enable traps
        CWP = 4,0           # Current window pointer


    class WIM(Register):    # Window invalid mask
        offset = 0x400008

    class TBR(Register):
        offset = 0x40000C
        TBA = 31, 12
        TT = 11, 4

    class PC(Register):
        offset = 0x400010

    class NPC(Register):
        offset = 0x400014

    class FSR(Register):
        offset = 0x400018

    class CPSR(Register):
        offset = 0x40001C

    class Trap(Register):
        offset = 0x400020
        EM = 12
        TYPE = 11,4

    class ASI(Register):
        offset = 0x400024
        ASI = 7,0

    class ASR17(Register):
        offset=0x400044
        NWIN = 4,0
        NWP = 7,5
        V8 = 8
        M = 9
        FP = 11,10
        LD = 12
        SV=13
        DW=14
        CF=16,15
        CS=17

    class WatchPoints(Block):
        offset = 0x400000 + 24 * 4
        size = 4 * 4 * 2

    class ASI2(Block):
        offset=0x700000
        size = 16

        class CCR(Register):
            offset = 0
            ICS = 1,0
            DCS = 3,2
            IF = 4
            DF = 5
            DP = 14
            IP = 15
            IB = 16
            FI = 21
            FD = 22
            DS = 23

        class ICFG(Register):
            offset = 0x8
            M = 3
            LRSTART = 11, 4
            LRSIZE = 15, 12
            LSIZE = 18, 16
            LR = 19
            SSIZE = 23, 20
            SETS = 26, 24
            SN = 27
            REPL = 29, 28
            CL = 30

        class DCFG(Register):
            offset = 0xC
            M = 3
            LRSTART = 11, 4
            LRSIZE = 15, 12
            LSIZE = 18, 16
            LR = 19
            SSIZE = 23, 20
            SETS = 26, 24
            SN = 27
            REPL = 29, 28
            CL = 30

    class ASIRAM(Block):
        offset=0x700000
        size = 0x100000

