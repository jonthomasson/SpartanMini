/************************************************************************/
/*                                                                      */
/*    dpcutil.h  --    Interface Declarations for DPCUTIL.DLL           */
/*                                                                      */
/************************************************************************/
/*    Author: Gene Apperson                                             */
/*    Copyright 2003, 2004, Digilent Inc.                               */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    applications programming interface to the Digilent DPCUTIL.DLL    */
/*                                                                      */
/*    This DLL provides API services to provide an interface for a      */
/*    configuration channel and a data channel into a Digilent System   */
/*    board using one of the Digilent Communications Interface Modules. */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  02/26/2003(GeneA): Created                                          */
/*  04/11/2005(Seth):  Added SPI interface                              */
/*  02/26/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DPCUTIL_INCLUDED)
#define      DPCUTIL_INCLUDED

#if !defined(DPCDEFS_INCLUDED)
    #include "dpcdefs.h"
#endif

#if !defined(DPCAPI)

    #if defined(WIN32)
        
        #if defined(__cplusplus)
            #define DPCAPI extern "C" __declspec(dllimport)
        #else
            #define DPCAPI __declspec(dllimport)
        #endif
        
    #else
        
        #if defined(__cplusplus)
            #define DPCAPI extern "C" __attribute__ ((visibility("default")))
        #else
            #define DPCAPI __attribute__ ((visibility("default")))
        #endif
        
    #endif
    
#endif

/* ------------------------------------------------------------ */
/*                Miscellaneous Declarations                    */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                Type Declarations                             */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                Interface Procedure Declarations              */
/* ------------------------------------------------------------ */

DPCAPI  BOOL    DpcInit(ERC * perc);
DPCAPI  void    DpcTerm(void);

DPCAPI  BOOL    DpcGetDpcVersion(char * szVersion, ERC *perc);

#if defined(WIN32)
DPCAPI  BOOL    DpcStartNotify(HWND hwndTemp, WORD idNotifyTemp, ERC *perc);
DPCAPI  BOOL    DpcEndNotify(HWND hwndTemp, ERC *perc);
#endif

DPCAPI  BOOL    DpcGetVersion(HANDLE hif, BYTE * rgbVersion, INT32 cbVersion, ERC * perc, TRID * ptrid);

DPCAPI  BOOL    DpcWaitForTransaction(HANDLE hif, TRID trid, ERC * perc);
DPCAPI  BOOL    DpcPendingTransactions(HANDLE hif, INT32 * pctran, ERC * perc);
DPCAPI  BOOL    DpcQueryConfigStatus(HANDLE hif, TRID trid, TRS * ptrs, ERC * perc);
DPCAPI  BOOL    DpcAbortConfigTransaction(HANDLE hif, TRID trid, ERC * perc);
DPCAPI  BOOL    DpcClearConfigStatus(HANDLE hif, TRID trid, ERC * perc);
DPCAPI  ERC     DpcGetFirstError(HANDLE hif);

// JTAG
DPCAPI  BOOL    DpcOpenJtag(HANDLE * phif, char * szdvc, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcCloseJtag(HANDLE hif, ERC * perc);
DPCAPI  BOOL    DpcEnableJtag(HANDLE hif, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcDisableJtag(HANDLE hif, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcSetJtagSpeed(HANDLE hif, INT32 cbData, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcSetTmsTdiTck(HANDLE hif, BOOL fTms, BOOL fTdi, BOOL fTck, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcPutTdiBits(HANDLE hif, INT32 cbit, BYTE * rgbSnd, BOOL bitTms, BOOL fReturnTdo, BYTE * rgbRcv, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcPutTmsTdiBits(HANDLE hif, INT32 cbit, BYTE * rgbSnd, BOOL fReturnTdo, BYTE * rgbRcv, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcGetTdoBits(HANDLE hif, INT32 cbits, BOOL bitTdi, BOOL bitTms, BYTE *rgbRcv, ERC *perc, TRID *ptrid);

// EPP
DPCAPI  BOOL    DpcOpenData(HANDLE * phif, char * szdvc, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcCloseData(HANDLE hif, ERC * perc);
DPCAPI  BOOL    DpcPutReg(HANDLE hif, BYTE bAddr, BYTE bData, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcGetReg(HANDLE hif, BYTE bAddr, BYTE * pbData, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcPutRegSet(HANDLE hif, BYTE * rgbAddr, BYTE * rgbData, INT32 cbData, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcGetRegSet(HANDLE hif, BYTE * rgbAddr, BYTE * rgbData, INT32 cbData, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcPutRegRepeat(HANDLE hif, BYTE bAddr, BYTE * rgbData, INT32 cbData, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcGetRegRepeat(HANDLE hif, BYTE bAddr, BYTE * rgbData, INT32 cbData, ERC * perc, TRID * ptrid);

// Stream
DPCAPI  BOOL    DpcStreamWrite(HANDLE hif, BYTE * rgbData, INT32 cbData, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcStreamRead(HANDLE hif, BYTE * rgbData, INT32 cbData, ERC * perc, TRID * ptrid);

// SPI
DPCAPI  BOOL    DpcOpenSpi(HANDLE * phif, char * szdvc, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcCloseSpi(HANDLE hif, ERC * perc);
DPCAPI  BOOL    DpcEnableSpi(HANDLE hif, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcDisableSpi(HANDLE hif, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcSetSpiSelect(HANDLE hif, INT32 idSel, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcSetSpiMode(HANDLE hif, INT32 idMode, INT32 idDir, INT32 idSpeed, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcSetSpiModeSpeed(HANDLE hif, INT32 idMode, INT32 idDir, INT32 idSpeed, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcPutSpiByte(HANDLE hif, BYTE bSnd, BYTE * pbRcv, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcPutSpi(HANDLE hif, INT32 cbSnd, BYTE * rgbSnd, BYTE * rgbRcv, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcGetSpi(HANDLE hif, INT32 cbRcv, BYTE bFill, BYTE * rgbRcv, ERC * perc, TRID * ptrid);

// PinIo
DPCAPI  BOOL    DpcEnablePinIo(HANDLE hif, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcDisablePinIo(HANDLE hif, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcGetPinMask(HANDLE hif, DWORD * pfsMask, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcSetPinDirection(HANDLE hif, DWORD fsDir, ERC * perc, TRID * ptrid);
DPCAPI  BOOL    DpcSetPinState(HANDLE hif, DWORD fsState, ERC * erc, TRID * ptrid);
DPCAPI  BOOL    DpcGetPinState(HANDLE hif, DWORD * pfsState, ERC * perc, TRID * ptrid);

/* Device Manager Functions.
** The device manager is used to maintain the table of Digilent
** interface modules installed in the system.
*/
#if defined(WIN32)
DPCAPI  void    DvmgStartConfigureDevices(HWND hWnd, ERC * perc);
#endif

DPCAPI  INT32   DvmgGetDevCount(ERC * perc);
DPCAPI  BOOL    DvmgGetDevName(INT32 idvc, char * szdvcTemp, ERC * perc);
DPCAPI  BOOL    DvmgGetDevType(INT32 idvc, INT32 * dvtp, ERC * perc);
DPCAPI  INT32   DvmgGetDefaultDev(ERC * perc);


/* ADDED 1/21/09  for JTSC workaround */
DPCAPI  BOOL    DpcSetDefPort(INT32 prt);

/* ------------------------------------------------------------ */

#endif                    // DPCUTIL_INCLUDED

/************************************************************************/
