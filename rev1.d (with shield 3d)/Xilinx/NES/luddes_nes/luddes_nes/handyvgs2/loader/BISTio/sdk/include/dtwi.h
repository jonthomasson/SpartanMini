/************************************************************************/
/*                                                                      */
/*  dtwi.h  --      Interface Declarations for DTWI.DLL                 */
/*                                                                      */
/************************************************************************/
/*  Author:     Gene Apperson                                           */
/*  Copyright 2008, Digilent Inc.                                       */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*  This header file contains the interface declarations for the API    */
/*  of the DTWI.DLL. This DLL provices API services to provide a TWI    */
/*  (I2C) compatible interface for the Digilent Adept Software System.  */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  05/19/2008(GeneA): created                                          */
/*  10/02/2008(GeneA): Added DtwiEnableEx                               */
/*  10/07/2008(GeneA): Added twicap definitions                         */
/*  10/30/2008(GeneA): changed twicap to dprpTwi and changed bit        */
/*      definitions.                                                    */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  02/26/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DTWI_INCLUDED)
#define      DTWI_INCLUDED

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
/*                  Miscellaneous Declarations                  */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*          TWI Capabilities Definitions                        */
/* ------------------------------------------------------------ */

/* Define the port property bits for TWI ports.
*/
const DPRP dprpTwiMaster        = 0x00000001;	// port supports TWI master operation
const DPRP dprpTwiSlave         = 0x00000002;   // port supports TWI slave capabilities
const DPRP dprpTwiMultiMaster   = 0x00000004;   // port supports multi-master arbitration
const DPRP dprpTwiBatch         = 0x00000008;   // port provides TWI batch support
const DPRP dprpTwiSetSpeed      = 0x00000010;   // port has settable clock speed
const DPRP dprpTwiSmbAlert      = 0x00000020;   // port supports SMB Alert pin
const DPRP dprpTwiSmbSuspend    = 0x00000040;   // port supports SMB Suspend pin
const DPRP dprpTwiSmbPEC        = 0x00000080;   // port supports SMB packet error checking
                                    
/* ------------------------------------------------------------ */
/*          TWI Batch Command Declarations                      */
/* ------------------------------------------------------------ */
/*
** Batch command protocol description
** Each command begins with the command code byte. Most commands are
** followed by one or two parameter bytes.
** The wait command is followed by the wait time in microseconds
** The Put command is followed by count of bytes to write, followed
** by the data bytes
** The Get command is followed by the count of bytes to read
**
** Cmd              Param       Param       Data bytes  
** byte             byte 1      byte 2
** =================================================
** tcbStop
** tcbStartSlaw     dadrSlave
** tcbStartSlar     dadrSlave
** tcbRepStartSlaw  dadrSlave
** tcbRepStartSlar  dadrSlave
** tcbPut           cbPutL      cbPutH      b1 b2 b3 ...
** tcbGet           cbGetL      cbGetH
** tcbWait          tusWaitL    tusWaitH
*/
#define tcbStop             0x11
#define tcbStartSlaw        0x22
#define tcbStartSlar        0x32
#define tcbRepStartSlaw     0x42
#define tcbRepStartSlar     0x52
#define tcbPut              0x63
#define tcbGet              0x73
#define tcbWait             0x83

/* ------------------------------------------------------------ */
/*                  General Type Declarations                   */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                  Object Class Declarations                   */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                  Variable Declarations                       */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                  Procedure Declarations                      */
/* ------------------------------------------------------------ */

/* Basic interface functions.
*/
DPCAPI BOOL DtwiGetVersion(char * szVersion);
DPCAPI BOOL DtwiGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI BOOL DtwiGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI BOOL DtwiEnable(HIF hif);
DPCAPI BOOL DtwiEnableEx(HIF hif, INT32 prtReq);
DPCAPI BOOL DtwiDisable(HIF hif);

DPCAPI BOOL DtwiSetSpeed(HIF hif, DWORD frqReq, DWORD * pfrqSet);
DPCAPI BOOL DtwiGetSpeed(HIF hif, DWORD * pfrqCur);

/* TWI Master data transfer functions.
*/
DPCAPI BOOL DtwiMasterPut(HIF hif, BYTE dadr, DWORD cbSnd, BYTE * rgbSnd, BOOL fOverlap);
DPCAPI BOOL DtwiMasterGet(HIF hif, BYTE dadr, DWORD cbRcv, BYTE * rgbRcv, BOOL fOverlap);
DPCAPI BOOL DtwiMasterPutGet(HIF hif, BYTE dadr, DWORD cbSnd, BYTE * rgbSnd, DWORD tusWait, DWORD cbRcv, BYTE * rgbRcv, BOOL fOverlap);
DPCAPI BOOL DtwiMasterBatch(HIF hif, DWORD cbSnd, BYTE * rgbSnd, DWORD cbRcv, BYTE * rgbRcv, BOOL fOverlap);

/* TWI Slave data transfer functions.
*/
DPCAPI BOOL DtwiSlaveEnable(HIF hif, BYTE dadr, BOOL fGeneralCall, BOOL FAck);
DPCAPI BOOL DtwiSlaveDisable(HIF hif);
DPCAPI BOOL DtwiSlaveQueryBuffer(HIF hif, DWORD * pcbTx, DWORD * pcbRx);
DPCAPI BOOL DtwiSlaveRxQuery(HIF hif, DWORD * pcbRx);
DPCAPI BOOL DtwiSlaveRxRead(HIF hif, DWORD cbRcvMax, BYTE * rgbRcv, DWORD * pcbRcv, BOOL fOverlap);
DPCAPI BOOL DtwiSlaveTxQuery(HIF hif, DWORD * pcbTx);
DPCAPI BOOL DtwiSlaveTxPost(HIF hif, DWORD cbTx, BYTE * rgbTx, BOOL fOverlap);

/* SM Bus functions.
*/
DPCAPI BOOL DtwiSmbQueryAlert(HIF hif, BOOL * pfAlert);
DPCAPI BOOL DtwiSmbSetSuspend(HIF hif, BOOL fSuspend);
DPCAPI BOOL DtwiSmbPecEnable(HIF hif);
DPCAPI BOOL DtwiSmbPecDisable(HIF hif);

/* ------------------------------------------------------------ */

#endif

/************************************************************************/
