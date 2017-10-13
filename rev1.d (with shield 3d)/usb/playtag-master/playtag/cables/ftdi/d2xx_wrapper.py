#! /usr/bin/env python
import sys
import os
import ctypes
from types import MethodType

windows = 'win' in sys.platform

if windows:
    libfile = 'ftd2xx'
    loader = ctypes.WinDLL
else:
    libfile = '/usr/lib/libftd2xx.so'
    loader = ctypes.CDLL
    if not os.path.exists(libfile):
        libfile = os.path.join(os.path.dirname(__file__), 'libftd2xx.so')

loaded = True
try:
    FtdiLibrary = loader(libfile)
except OSError:
    loaded = False
    class FtdiLibrary(object):
        def __getattr__(self, name):
            class Unloaded(object):
                def __init__(*whatever):
                    raise OSError("%s called, but library %s could not be loaded" % (name, libfile))
            return Unloaded
    FtdiLibrary = FtdiLibrary()

StatusTypes = '''
    FT_OK,
    FT_INVALID_HANDLE,
    FT_DEVICE_NOT_FOUND,
    FT_DEVICE_NOT_OPENED,
    FT_IO_ERROR,
    FT_INSUFFICIENT_RESOURCES,
    FT_INVALID_PARAMETER,
    FT_INVALID_BAUD_RATE,
    FT_DEVICE_NOT_OPENED_FOR_ERASE,
    FT_DEVICE_NOT_OPENED_FOR_WRITE,
    FT_FAILED_TO_WRITE_DEVICE,
    FT_EEPROM_READ_FAILED,
    FT_EEPROM_WRITE_FAILED,
    FT_EEPROM_ERASE_FAILED,
    FT_EEPROM_NOT_PRESENT,
    FT_EEPROM_NOT_PROGRAMMED,
    FT_INVALID_ARGS,
    FT_NOT_SUPPORTED,
    FT_OTHER_ERROR
'''

DeviceTypes = '''
    FT_DEVICE_BM,
    FT_DEVICE_AM,
    FT_DEVICE_100AX,
    FT_DEVICE_UNKNOWN,
    FT_DEVICE_2232C,
    FT_DEVICE_232R,
    FT_DEVICE_2232H,
    FT_DEVICE_4232H,
    FT_DEVICE_232H
'''

StatusTypes = dict(enumerate(StatusTypes.replace(',', ' ').split()))
DeviceTypes = dict(enumerate(DeviceTypes.replace(',', ' ').split()))


class func(tuple):
    def __new__(cls, *values):
        return tuple.__new__(cls, values)

def errcheck(result, func, args):
    if not result:
        return
    errcode = StatusTypes.get(result, 'Unknown Error')
    raise SystemExit("FTDI Driver error in function %s: %s (%d)" % (func.__name__, errcode, result))

BASE_HANDLE = ctypes.c_void_p
class HANDLE(object):
    pass

class FT(BASE_HANDLE):

    StatusTypes = StatusTypes
    DeviceTypes = DeviceTypes
    loaded = loaded

    OPEN_BY_SERIAL_NUMBER    = 1
    OPEN_BY_DESCRIPTION      = 2
    OPEN_BY_LOCATION         = 4
    LIST_NUMBER_ONLY         = 0x80000000
    LIST_BY_INDEX            = 0x40000000
    LIST_ALL                 = 0x20000000
    LIST_MASK                =  LIST_NUMBER_ONLY | LIST_BY_INDEX | LIST_ALL
    BAUD_300         = 300
    BAUD_600         = 600
    BAUD_1200        = 1200
    BAUD_2400        = 2400
    BAUD_4800        = 4800
    BAUD_9600        = 9600
    BAUD_14400       = 14400
    BAUD_19200       = 19200
    BAUD_38400       = 38400
    BAUD_57600       = 57600
    BAUD_115200      = 115200
    BAUD_230400      = 230400
    BAUD_460800      = 460800
    BAUD_921600      = 921600
    BITS_8           = 8
    BITS_7           = 7
    STOP_BITS_1      = 0
    STOP_BITS_2      = 2
    PARITY_NONE      = 0
    PARITY_ODD       = 1
    PARITY_EVEN      = 2
    PARITY_MARK      = 3
    PARITY_SPACE     = 4
    FLOW_NONE        = 0x0000
    FLOW_RTS_CTS     = 0x0100
    FLOW_DTR_DSR     = 0x0200
    FLOW_XON_XOFF    = 0x0400
    PURGE_RX         = 1
    PURGE_TX         = 2
    EVENT_RXCHAR         = 1
    EVENT_MODEM_STATUS   = 2
    EVENT_LINE_STATUS    = 4
    DEFAULT_RX_TIMEOUT   = 300
    DEFAULT_TX_TIMEOUT   = 300
    BITMODE_RESET                = 0x00
    BITMODE_ASYNC_BITBANG        = 0x01
    BITMODE_MPSSE                = 0x02
    BITMODE_SYNC_BITBANG         = 0x04
    BITMODE_MCU_HOST             = 0x08
    BITMODE_FAST_SERIAL          = 0x10
    BITMODE_CBUS_BITBANG         = 0x20
    BITMODE_SYNC_FIFO            = 0x40

    byref = ctypes.byref
    POINTER = ctypes.POINTER
    LPVOID = PVOID = ctypes.c_void_p

    USHORT = ctypes.c_ushort
    UCHAR = ctypes.c_ubyte
    CHAR = ctypes.c_char
    INT = ctypes.c_int

    if windows:
        from ctypes.wintypes import DWORD, ULONG, BOOL, LONG, UINT
    else:
        # Goofy definitions from FTDI's WinTypes.h...
        DWORD = ULONG = BOOL = LONG = UINT = ctypes.c_uint

    LPDWORD = POINTER(DWORD)
    PULONG = POINTER(ULONG)
    PUCHAR = POINTER(UCHAR)

    class DEVICE_LIST_INFO_NODE(ctypes.Structure):
        pass
    DEVICE_LIST_INFO_NODE._fields_ = [
            ('Flags', DWORD),
            ('Type', DWORD),
            ('ID', DWORD),
            ('LocID', DWORD),
            ('SerialNumber', CHAR * 16),
            ('Description', CHAR * 64),
            ('ftHandle', BASE_HANDLE),
        ]

    ListDevices = func(PVOID, PVOID, DWORD)
    if windows:
        GetComPortNumber = func(HANDLE, PULONG)
    else:
        SetVIDPID = func(DWORD, DWORD)
        GetVIDPID = func(LPDWORD, LPDWORD)
    CreateDeviceInfoList = func(LPDWORD)
    GetDeviceInfoList = func(POINTER(DEVICE_LIST_INFO_NODE), LPDWORD)
    Open = func(INT, POINTER(BASE_HANDLE))
    OpenEx = func(PVOID, DWORD, POINTER(BASE_HANDLE))
    Close = func(HANDLE)
    Read = func(HANDLE, LPVOID, DWORD, LPDWORD)
    Write = func(HANDLE, LPVOID, DWORD, LPDWORD)
    SetBaudRate = func(HANDLE, ULONG)
    SetDivisor = func(HANDLE, USHORT)
    SetDataCharacteristics = func(HANDLE, UCHAR, UCHAR, UCHAR)
    SetFlowControl = func(HANDLE, USHORT, UCHAR, UCHAR)
    ResetDevice = func(HANDLE)
    SetDtr = func(HANDLE)
    ClrDtr = func(HANDLE)
    SetRts = func(HANDLE)
    ClrRts = func(HANDLE)
    GetModemStatus = func(HANDLE, PULONG)
    SetChars = func(HANDLE, UCHAR, UCHAR, UCHAR, UCHAR)
    Purge = func(HANDLE, ULONG)
    SetTimeouts = func(HANDLE, ULONG, ULONG)
    GetQueueStatus = func(HANDLE, LPDWORD)
    SetEventNotification = func(HANDLE, DWORD, PVOID)
    GetStatus = func(HANDLE, LPDWORD, LPDWORD, LPDWORD)
    SetBreakOn = func(HANDLE)
    SetBreakOff = func(HANDLE)
    SetWaitMask = func(HANDLE, DWORD)
    WaitOnMask = func(HANDLE, LPDWORD)
    GetEventStatus = func(HANDLE, LPDWORD)
    SetLatencyTimer = func(HANDLE, UCHAR)
    GetLatencyTimer = func(HANDLE, PUCHAR)
    SetBitMode = func(HANDLE, UCHAR, UCHAR)
    GetBitMode = func(HANDLE, PUCHAR)
    SetUSBParameters = func(HANDLE, ULONG, ULONG)
    StopInTask = func(HANDLE)
    RestartInTask = func(HANDLE)
    SetResetPipeRetryCount = func(HANDLE, DWORD)
    ResetPort = func(HANDLE)

def FixClass(FT, isinstance=isinstance, list=list, getattr=getattr, setattr=setattr, HANDLE=HANDLE, BASE_HANDLE=BASE_HANDLE):
    ''' Could use a metaclass, but this is almost too simple, and only
        one class needs the treatment.
    '''
    funcs = [x for x in vars(FT).iteritems() if isinstance(x[1], func)]
    for mydict in (StatusTypes, DeviceTypes):
        for value, name in mydict.iteritems():
            setattr(FT, name[3:], value)
    STATUS = FT.ULONG
    for attrname, value in funcs:
        value = list(value)
        ismethod = value[0] is HANDLE
        if ismethod:
            value[0] = BASE_HANDLE
        libfunc = getattr(FtdiLibrary, 'FT_' + attrname)
        libfunc.argtypes = value
        libfunc.restype = STATUS
        libfunc.errcheck = errcheck
        if ismethod:
            libfunc = MethodType(libfunc, None, FT)
        setattr(FT, attrname, libfunc)

FixClass(FT)
