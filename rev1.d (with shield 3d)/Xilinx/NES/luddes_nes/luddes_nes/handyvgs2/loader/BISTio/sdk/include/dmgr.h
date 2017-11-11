/************************************************************************/
/*                                                                      */
/*    dmgr.h  --    Public Interface Declarations for DMGR.DLL          */
/*                                                                      */
/************************************************************************/
/*    Author: Joshua Pederson                                           */
/*    Copyright 2008 Digilent Inc.                                      */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    public enumeration and device list services in the Digilent       */
/*    dpcomm.DLL                                                        */
/*                                                                      */
/*    This DLL provides API services to provide the transport layer     */
/*    for all Adept2 application protocols.                             */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  04/23/2007(JPederson): Created                                      */
/*  07/23/2007(JPederson): changed name to conn.h (from dvc.h)          */
/*  08/15/2007(JPederson):  changed File and API name to dmgr           */
/*  02/17/2010(GeneA): added DmgrSetInfo                                */
/*  04/21/2010(MichaelA): added function DmgrGetDvcFromHif for getting  */
/*      a DVC from a handle to an open device                           */
/*                                                                      */
/************************************************************************/

#if !defined(DMGR_INCLUDED)
#define      DMGR_INCLUDED

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
/*                  General Type Declarations                   */
/* ------------------------------------------------------------ */

/* The following value is passed to DmgrGetTransResult to specify
** wait until the transfer completes.
*/
const DWORD		tmsWaitInfinite = 0xFFFFFFFF;

/* ------------------------------------------------------------ */
/*                  Object Class Declarations                   */
/* ------------------------------------------------------------ */

/* ------------------------------------------------------------ */
/*                  Variable Declarations                       */
/* ------------------------------------------------------------ */

/* ------------------------------------------------------------ */
/*                Interface Procedure Declarations              */
/* ------------------------------------------------------------ */

DPCAPI  BOOL    DmgrGetVersion(char * szVersion);
//DmgrGetLastError returns the last error per process which is updated when a DVC API function fails.
DPCAPI  ERC     DmgrGetLastError();
DPCAPI  BOOL    DmgrSzFromErc(ERC erc, char * szErc, char * szErcMessage);

//OPEN & CLOSE functions
DPCAPI  BOOL    DmgrOpen(HIF * phif, char * szSel); 
DPCAPI  BOOL    DmgrOpenEx(HIF * phif, char * szSel, DTP dtpTable, DTP dtpDisc);
DPCAPI  BOOL    DmgrClose(HIF hif);

//ENUMERATION functions
DPCAPI  BOOL    DmgrEnumDevices(int * pcdvc);
DPCAPI  BOOL    DmgrEnumDevicesEx(int * pcdvc, DTP dtpTable, DTP dtpDisc, DINFO dinfoSel, void* pInfoSel);
DPCAPI  BOOL    DmgrStartEnum(DTP dtpTable, DTP dtpDisc, DINFO dinfoSel, void * pInfoSel);
DPCAPI  BOOL    DmgrIsEnumFinished();
DPCAPI  BOOL    DmgrStopEnum();
DPCAPI  BOOL    DmgrGetEnumCount(int * pcdvc);
DPCAPI  BOOL    DmgrGetDvc(int idvc, DVC * pdvc);
DPCAPI  BOOL    DmgrFreeDvcEnum();

//TRANSFER status and control functions
DPCAPI  BOOL    DmgrGetTransResult(HIF hif, DWORD* pdwDataOut, DWORD* pdwDataIn, DWORD tmsWait);
DPCAPI  BOOL    DmgrCancelTrans(HIF hif);
DPCAPI  BOOL    DmgrSetTransTimeout(HIF hif, DWORD tmsTimeout);
DPCAPI  BOOL    DmgrGetTransTimeout(HIF hif, DWORD* ptmsTimeout);

//DVC Table manipulation functions
#if defined (WIN32)
DPCAPI  BOOL    DmgrOpenDvcMg(HWND hwnd);  //opens device manager dialog box
#endif

DPCAPI  BOOL    DmgrDvcTblAdd(DVC * pdvc);
DPCAPI  BOOL    DmgrDvcTblRem(char * szAlias);
DPCAPI  BOOL    DmgrDvcTblSave();

//Device transport type management functions
DPCAPI  int     DmgrGetDtpCount();
DPCAPI  BOOL    DmgrGetDtpFromIndex(int idtp, DTP * pdtp);
DPCAPI  BOOL    DmgrGetDtpString(DTP dtp, char* szDtpString);

//Miscellaneous functions
DPCAPI  BOOL    DmgrSetInfo(DVC * pdvc, DINFO dinfo, void * pvInfoSet);
DPCAPI  BOOL    DmgrGetInfo(DVC * pdvc, DINFO dinfo, void * pvInfoGet);

DPCAPI  BOOL    DmgrGetDvcFromHif(HIF hif, DVC* pdvc);

/* ------------------------------------------------------------ */

#endif                    // DMGR_INCLUDED

/************************************************************************/
