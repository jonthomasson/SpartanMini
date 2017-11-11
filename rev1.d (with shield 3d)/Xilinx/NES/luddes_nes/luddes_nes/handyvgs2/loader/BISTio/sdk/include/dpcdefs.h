/************************************************************************/
/*                                                                      */
/*  dpcdefs.h  --   Type and constant definitions for DPCUTIL.DLL       */
/*                                                                      */
/************************************************************************/
/*  Author:     Gene Apperson                                           */
/*  Copyright 2003, 2004, Digilent, Inc.                                */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*  General symbol and type definitions used by the Digilent DPCUTIL    */
/*  and JTSC DLL's.                                                     */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  04/10/2003(Seth): Created                                           */
/*  07/22/2004(GeneA): cleaned up for initial public release            */
/*                                                                      */
/************************************************************************/

#if !defined(DPCDEFS_INCLUDED)
#define DPCDEFS_INCLUDED

/* ------------------------------------------------------------ */
/*              Type Declarations                               */
/* ------------------------------------------------------------ */

typedef WORD    TRID;   /* Transaction ID type */
typedef int     ERC;    /* Error code type */
typedef int     TRT;    /* Transaction type */
typedef int     STS;    /* Transaction status type */
typedef int     IFD;    /* Interface ID */
typedef long    IFP;

typedef int     DVCT;   /*Interface device type*/

/* Transaction status structure, 
** holds status information about a transaction 
*/

#pragma pack(8)
typedef struct tagTRS {
    TRT     trt;        /* transaction type */
    TRID    trid;       /* transaction ID */
    STS     sts;        /* status of transaction */
    ERC     erc;        /* error code for transaction */
}TRS;
#pragma pack()

/* ------------------------------------------------------------ */
/*              Constant Declarations                           */
/* ------------------------------------------------------------ */

const int   cchDevNameMax = 28;


/* Transaction type codes
*/
const TRT trtOpenJtag           = 0x01;
const TRT trtCloseJtag          = 0x02;
const TRT trtSetTmsTdiTck       = 0x03;
const TRT trtPutTdiBits         = 0x04;
const TRT trtPutTmsTdiBits      = 0x05;
const TRT trtGetTdoBits         = 0x06;
const TRT trtSetJtsel           = 0x07;
const TRT trtOpenSpi            = 0x21;
const TRT trtCloseSpi           = 0x22;
const TRT trtEnableSpi          = 0x23;
const TRT trtDisableSpi         = 0x24;
const TRT trtSetSpiSelect       = 0x25;
const TRT trtSetSpiMode         = 0x26;
const TRT trtPutSpiByte         = 0x27;
const TRT trtPutSpi             = 0x28;
const TRT trtGetSpi             = 0x29;
const TRT trtSetJtagSpeed       = 0x2a;
const TRT trtEnablePinIo        = 0x2b;
const TRT trtDisablePinIo       = 0x2c;
const TRT trtGetPinMask         = 0x2d;
const TRT trtSetPinDirection    = 0x2e;
const TRT trtSetPinState        = 0x2f;
const TRT trtGetPinState        = 0x30;

const TRT trtOpenData           = 0x81;
const TRT trtCloseData          = 0x82;
const TRT trtSetDataPins        = 0x83;
const TRT trtGetDataPins        = 0x84;
const TRT trtSendDataByte       = 0x85;
const TRT trtGetDataByte        = 0x86;
const TRT trtSendDataBytes      = 0x87;
const TRT trtGetDataBytes       = 0x88;
const TRT trtSendDataStream     = 0x89;
const TRT trtGetDataStream      = 0x8a;
const TRT trtSendGetDataBytes   = 0x8b;
const TRT trtGetVersion         = 0x8c;
const TRT trtStreamWrite        = 0x8d;
const TRT trtStreamRead         = 0x8e;
const TRT trtSetSpiModeSpeed    = 0x8f;


const DVCT dvctEthernet         = 0x00;
const DVCT dvctUSB              = 0x01;
const DVCT dvctSerial           = 0x02;
const DVCT dvctParallel         = 0x03;


/* Error codes
*/
const ERC ercNoError        = 0;
const ERC ercConnReject     = 3001;
const ERC ercConnType       = 3002;
const ERC ercConnNoMode     = 3003;
const ERC ercInvParam       = 3004;
const ERC ercInvCmd         = 3005;
const ERC ercUnknown        = 3006;
const ERC ercJtagConflict   = 3007;
const ERC ercNotImp         = 3008;
const ERC ercNoMem          = 3009;
const ERC ercTimeout        = 3010;
const ERC ercConflict       = 3011;
const ERC ercBadPacket      = 3012;
const ERC ercInvOption      = 3013;
const ERC ercAlreadyCon     = 3014;
const ERC ercConnected      = 3101;
const ERC ercNotInit        = 3102;
const ERC ercCantConnect    = 3103;
const ERC ercAlreadyConnect = 3104;
const ERC ercSendError      = 3105;
const ERC ercRcvError       = 3106;
const ERC ercAbort          = 3107;
const ERC ercTimeOut        = 3108;
const ERC ercOutOfOrder     = 3109;
const ERC ercExtraData      = 3110;
const ERC ercMissingData    = 3111;
const ERC ercTridNotFound   = 3201;
const ERC ercNotComplete    = 3202;
const ERC ercNotConnected   = 3203;
const ERC ercWrongMode      = 3204;
const ERC ercWrongVersion   = 3205;
const ERC ercDvctableDne    = 3301;
const ERC ercDvctableCorrupt= 3302;
const ERC ercDvcDne         = 3303;
const ERC ercDpcutilInitFail= 3304;
const ERC ercUnknownErr     = 3305;
const ERC ercDvcTableOpen   = 3306;
const ERC ercRegError       = 3307;
const ERC ercNotifyRegFull  = 3308;
const ERC ercNotifyNotFound = 3309;
const ERC ercOldDriverNewFw = 3310;
const ERC ercInvHandle      = 3311;
const ERC ercInterfaceNotSupported = 3312;

/* Transaction status codes
*/
const STS stsNew        = 1;
const STS stsRunning    = 2;
const STS stsComplete   = 3;

/* ------------------------------------------------------------ */

#endif                  // DPCDEFS_INCLUDED

/************************************************************************/
