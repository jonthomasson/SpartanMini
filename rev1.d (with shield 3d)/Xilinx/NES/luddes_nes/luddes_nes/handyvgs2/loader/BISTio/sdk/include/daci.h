/************************************************************************/
/*                                                                      */
/*  daci.h  --      Interface Declarations for DACI.DLL                 */
/*                                                                      */
/************************************************************************/
/*  Author:     Gene Apperson                                           */
/*  Copyright 2009, Digilent Inc.                                       */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*  This header file contains the interface declarations for the API    */
/*  of the DACI.DLL. This DLL provices API services for asynchronous    */
/*  serial communications.                                              */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  06/24/2009(GeneA): created                                          */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  02/25/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DACI_INCLUDED)
#define      DACI_INCLUDED

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
/*          EMC Port Properties Definitions                     */
/* ------------------------------------------------------------ */

/* Define the port property bits for ACI ports.
*/
const DPRP dprpAciDte           = 0x00000001;   // port implements a DTE device
const DPRP dprpAciDce           = 0x00000002;   // port implements a DCE device
const DPRP dprpAciRtsCts        = 0x00000004;   // port supports RTS/CTS handshaking
const DPRP dprpAciXonXoff       = 0x00000008;   // port supports XON/XOFF handshaking
const DPRP dprpAciBaudRate      = 0x00000010;   // port supports setting baud rate
const DPRP dprpAciStopBits      = 0x00000020;   // port supports setting number of stop bits
const DPRP dprpAciDataBits      = 0x00000040;   // port supports setting number of data bits
const DPRP dprpAciParityNone    = 0x00000080;   // port supports setting parity none
const DPRP dprpAciParityOdd     = 0x00000100;   // port supports setting odd parity
const DPRP dprpAciParityEven    = 0x00000200;   // port supports setting even parity
const DPRP dprpAciParityMark    = 0x00000400;   // port supports setting mark parity
const DPRP dprpAciParitySpace   = 0x00000800;   // port supports setting space parity

const DPRP dprpAciParityAll     = dprpAciParityOdd|dprpAciParityEven|dprpAciParityMark|dprpAciParitySpace;

/* Define symbols used in API functions.
*/
const int   cbtAciDataMin       = 5;    //minumum number of data bits allowed
const int   cbtAciDataMax       = 8;    //maximum number of data bits allowed

const int   idAciParityNone     = 0;
const int   idAciParityOdd      = 1;
const int   idAciParityEven     = 2;
const int   idAciParityMark     = 3;
const int   idAciParitySpace    = 4;

const int   idAciOneStopBit     = 1;
const int   idAciOne5StopBit    = 2;
const int   idAciTwoStopBit     = 3;

/* Define values returned in pdwStatus by the DaciQueryStatus function.
*/
const DWORD mskAciStsTxHalt     = 0x00000001;   //transmit buffer is halted
const DWORD mskAciStsRxBlock    = 0x00000002;   //receive buffer is in blocking mode
const DWORD mskAciStsTxStall    = 0x00000004;   //transmit is stalled due to flow control
const DWORD mskAciStsRxStall    = 0x00000008;   //receive is stalled due to flow control
const DWORD mskAciStsTxFcEnable = 0x00000010;   //transmit flow control enabled
const DWORD mskAciStsRxFcEnable = 0x00000020;   //receive flow control enabled

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
DPCAPI BOOL DaciGetVersion(char * szVersion);
DPCAPI BOOL DaciGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI BOOL DaciGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI BOOL DaciEnable(HIF hif);
DPCAPI BOOL DaciEnableEx(HIF hif, INT32 prtReq);
DPCAPI BOOL DaciDisable(HIF hif);

DPCAPI BOOL DaciGetMode(HIF hif, INT32 * pcbtData, INT32 * pidStop, INT32 * pidParity);
DPCAPI BOOL DaciSetMode(HIF hif, INT32 cbtData, INT32 idStop, INT32 idParity);
DPCAPI BOOL DaciGetBaud(HIF hif, ULONG * pbdrCur);
DPCAPI BOOL DaciSetBaud(HIF hif, ULONG bdrReq, ULONG * pbdrSet);
DPCAPI BOOL DaciGetBufferSize(HIF hif, ULONG * pcbTx, ULONG * pcbRx);
DPCAPI BOOL DaciSetRtsCtsEnable(HIF hif, BOOL fEnable);
DPCAPI BOOL DaciSetXonXoffEnable(HIF hif, BOOL fEnable);
DPCAPI BOOL DaciQueryStatus(HIF hif, ULONG * pcbTx, ULONG * pcbRx, DWORD * pdwStatus);
DPCAPI BOOL DaciHaltTx(HIF hif, BOOL fHalt);
DPCAPI BOOL DaciSetRxBlock(HIF hif, BOOL fBlock);
DPCAPI BOOL DaciPurgeBuffer(HIF hif, BOOL fTx, BOOL fRx);
DPCAPI BOOL DaciPutChar(HIF hif, BYTE bSnd, BOOL fOverlap);
DPCAPI BOOL DaciGetChar(HIF hif, BYTE * pbRcv, BOOL fOverlap);
DPCAPI BOOL DaciPutBuf(HIF hif, BYTE * rgchSnd, ULONG cchReq, BOOL fOverlap);
DPCAPI BOOL DaciGetBuf(HIF hif, BYTE * rgchRcv, ULONG cchReq, ULONG * pcchRcv, BOOL fOverlap);

/* ------------------------------------------------------------ */

#endif

/************************************************************************/
