#! /usr/bin/env python
import ctypes
from discover import driver
from playtag.lib.transport import connection
from playtag.iotemplate import IOTemplate, TDIVariable

'''
This program builds on the discover module.  After the cable
and chain are discovered, it runs a server that can be used
by Xilinx tools for jtag, as discussed here:

http://debugmo.de/2012/02/xvcd-the-xilinx-virtual-cable-daemon/
https://github.com/tmbinc/xvcd/tree/ftdi/src

For example, to use this with impact, choose cable setup, then
check the "Open Cable Plug-in" box, and enter the following
text in the dialog below there:

xilinx_xvc host=localhost:2542 disableversioncheck=true

Because the Xilinx tools themselves already know about the
JTAG protocol, this code plays dumb.  If the issue discussed
in that first website crops up with current versions of Xilinx
tools, then we can modify the code to fix the Xilinx bug.
'''

def getcmdinfo(data, constlen, tdivar=TDIVariable()):
    numbytes = len(data) - constlen

    class CmdStruct(ctypes.LittleEndianStructure):
        _pack_ = 1
        _fields_ = (
                ("cmdstr",   ctypes.c_char * 6),
                ("numbits",  ctypes.c_uint32),
                ("tmsbytes", ctypes.c_uint8 * numbytes),
        )

    class TdioStruct(ctypes.LittleEndianStructure):
        _pack_ = 1
        _fields_ = (
                ("data",    (numbytes + 7) / 8 * ctypes.c_uint64),
        )

    cmdinfo = CmdStruct.from_buffer_copy(data)
    numbits = cmdinfo.numbits
    tmsbuf = cmdinfo.tmsbytes
    bitmap = [min(numbits-i, 64) for i in range(0, numbits, 64)]

    assert cmdinfo.cmdstr == 'shift:', cmdinfo.cmdstr
    assert (numbits + 7) // 8 == numbytes, (numbits, numbytes)

    template = IOTemplate(driver)
    template.tms = [((tmsbuf[i/8] >> (i % 8)) & 1) for i in range(numbits)]
    template.tdi = [(j, tdivar) for j in bitmap]
    template.tdo = [(i>0 and 64 or 0, j) for (i,j) in enumerate(bitmap)]

    StrClass = ctypes.c_char * numbytes
    tdodata = TdioStruct()
    tdidata = TdioStruct()
    tdodata64 = tdodata.data
    tdidata64 = tdidata.data
    tdodatach = StrClass.from_buffer(tdodata)
    tdidatach = StrClass.from_buffer(tdidata)

    tdimask = (2 << ((numbits-1) % 64)) - 1

    def run_jtag(data):
        tdidatach.value = data[constlen:]
        tdidata64[-1] &= tdimask
        tdodata64[:] = list(template(tdidata64))
        return tdodatach.raw

    return run_jtag

def cmdproc(read, write, len=len, True=True):
    class CmdStruct(ctypes.LittleEndianStructure):
        _pack_ = 1
        _fields_ = (
                ("cmdstr",   ctypes.c_char * 6),
                ("numbits",  ctypes.c_uint32),
        )
    cmdstructsize = ctypes.sizeof(CmdStruct)

    cmdcache = {}
    cmdcacheget = cmdcache.get
    while True:
        data = ''
        while len(data) < cmdstructsize:
            newdata = read()
            if not newdata:
                return
            data += newdata
        cmdinfo = CmdStruct.from_buffer_copy(data)
        assert cmdinfo.cmdstr == 'shift:', cmdinfo.cmdstr
        numbits = cmdinfo.numbits
        numbytes = (cmdinfo.numbits + 7) // 8
        constlen = cmdstructsize + numbytes
        while len(data) < constlen + numbytes:
            data += read()
        run_jtag = cmdcacheget(data[:constlen])
        if run_jtag is None:
            run_jtag = cmdcache[data[:constlen]] = getcmdinfo(data, constlen)
        write(run_jtag(data))

connection(cmdproc, 'xvc', 2542, readsize=4096, logpackets=False)
