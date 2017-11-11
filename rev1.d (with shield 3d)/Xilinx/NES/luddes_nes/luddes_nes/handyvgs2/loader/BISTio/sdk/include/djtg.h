/************************************************************************/
/*                                                                      */
/*    djtg.h  --    Interface Declarations for djtg.DLL                 */
/*                                                                      */
/************************************************************************/
/*    Author: Joshua Pederson                                           */
/*    Copyright 2007 Digilent Inc.                                      */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    applications programming interface to the Digilent djtg.DLL       */
/*                                                                      */
/*    This DLL provides API services to provide the JTAG                */
/*    application protocol for Adept2.                                  */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  04/23/2007(JPederson): Created                                      */
/*  08/15/2007(JPederson):  changed File and API name to djtg           */
/*  10/01/2008(GeneA): Added DjtgEnableEx                               */
/*  10/22/2008(GeneA): Added functions DjtgGetPortCount and             */
/*      DjtgGetPortCapabilities                                         */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  02/25/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DJTG_INCLUDED)
#define      DJTG_INCLUDED

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
/*                  General Type Declarations                   */
/* ------------------------------------------------------------ */

/* Define port properties bits for JTAG ports.
*/
const DPRP  dprpJtgSetSpeed     = 0x00000001;   //port supports set speed call
const DPRP  dprpJtgSetPinState  = 0x00000002;   //device fully implements
                                                // DjtgSetTmsTdiTck 

/* ------------------------------------------------------------ */
/*                  Object Class Declarations                   */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                  Variable Declarations                       */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                Interface Procedure Declarations              */
/* ------------------------------------------------------------ */

DPCAPI BOOL DjtgGetVersion(char * szVersion);
DPCAPI BOOL DjtgGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI BOOL DjtgGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp);
DPCAPI BOOL DjtgEnable(HIF hif);
DPCAPI BOOL DjtgEnableEx(HIF hif, INT32 prtReq);
DPCAPI BOOL DjtgDisable(HIF hif);

//configuration functions
DPCAPI BOOL DjtgGetSpeed(HIF hif, DWORD * pfrqCur);
DPCAPI BOOL DjtgSetSpeed(HIF hif, DWORD frqReq, DWORD * pfrqSet);
DPCAPI BOOL DjtgSetTmsTdiTck(HIF hif, BOOL fTms, BOOL fTdi, BOOL fTck);
DPCAPI BOOL DjtgGetTmsTdiTdoTck(HIF hif, BOOL* pfTms, BOOL* pfTdi, BOOL* pfTdo, BOOL* pfTck);

//overlapped functions
DPCAPI BOOL DjtgPutTdiBits(HIF hif, BOOL fTms, BYTE * rgbSnd, BYTE * rgbRcv, DWORD cbits, BOOL fOverlap);
DPCAPI BOOL DjtgPutTmsBits(HIF hif, BOOL fTdi, BYTE * rgbSnd, BYTE * rgbRcv, DWORD cbits, BOOL fOverlap);
DPCAPI BOOL DjtgPutTmsTdiBits(HIF hif, BYTE * rgbSnd, BYTE * rgbRcv, DWORD cbitpairs, BOOL fOverlap);
DPCAPI BOOL DjtgGetTdoBits(HIF hif, BOOL fTdi, BOOL fTms, BYTE * rgbRcv, DWORD cbits, BOOL fOverlap);
DPCAPI BOOL DjtgClockTck(HIF hif, BOOL fTms, BOOL fTdi, DWORD cclk, BOOL fOverlap);

/* ------------------------------------------------------------ */

#endif                    // DJTG_INCLUDED

/************************************************************************/


