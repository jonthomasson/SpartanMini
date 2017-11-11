/************************************************************************/
/*                                                                      */
/*    dspi.h  --    Interface Declarations for DSPI.DLL                 */
/*                                                                      */
/************************************************************************/
/*    Author: Joshua Pederson                                           */
/*    Copyright 2007 Digilent Inc.                                      */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    applications programming interface to the Digilent dspi.DLL       */
/*                                                                      */
/*    This DLL provides API services to provide the SPI                 */
/*    application protocol for Adept2.                                  */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  04/23/2007(JPederson): Created                                      */
/*  10/01/2008(GeneA): Added DspiEnableEx                               */
/*  03/06/2009(GeneA): Added DspiSetDelay & DspiGetDelay                */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  02/26/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DSPI_INCLUDED)
#define      DSPI_INCLUDED

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

/* Define the property bits for SPI ports.
*/
const DPRP dprpSpiSetSpeed      = 0x00000001; //port supports setting SPI clock rate
const DPRP dprpSpiShiftLeft     = 0x00000002; //port supports MSB first shift
const DPRP dprpSpiShiftRight    = 0x00000004; //port supports LSB first shift
const DPRP dprpSpiDelay         = 0x00000008; //port supports inter-byte delay
const DPRP dprpSpiMode0         = 0x00000010; //port supports SPI mode 0
const DPRP dprpSpiMode1         = 0x00000020; //port supports SPI mode 1
const DPRP dprpSpiMode2         = 0x00000040; //port supports SPI mode 2
const DPRP dprpSpiMode3         = 0x00000080; //port supports SPI mode 3

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
/*                Interface Procedure Declarations                */
/* ------------------------------------------------------------ */

DPCAPI  BOOL    DspiGetVersion(char * szVersion);
DPCAPI  BOOL    DspiGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI  BOOL    DspiGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI  BOOL    DspiEnable(HIF hif);
DPCAPI  BOOL    DspiEnableEx(HIF hif, INT32 prtReq);
DPCAPI  BOOL    DspiDisable(HIF hif);

//configuration functions
DPCAPI  BOOL    DspiSetSelect(HIF hif, BOOL fSel);
DPCAPI  BOOL    DspiSetSpiMode(HIF hif, DWORD idMod, BOOL fShRight);
DPCAPI  BOOL    DspiGetSpeed(HIF hif, DWORD * pfrqCur);
DPCAPI  BOOL    DspiSetSpeed(HIF hif, DWORD frqReq, DWORD * pfrqSet);
DPCAPI  BOOL    DspiSetDelay(HIF hif, DWORD tusDelay);
DPCAPI  BOOL    DspiGetDelay(HIF hif, DWORD * ptusDelay);

//overlapped functions
DPCAPI  BOOL    DspiPutByte(HIF hif, BOOL fSelStart, BOOL fSelEnd, BYTE bSnd, BYTE * pbRcv, BOOL fOverlap);
DPCAPI  BOOL    DspiPut(HIF hif, BOOL fSelStart, BOOL fSelEnd, BYTE * rgbSnd, BYTE * rgbRcv, DWORD cbSnd, BOOL fOverlap);
DPCAPI  BOOL    DspiGet(HIF hif, BOOL fSelStart, BOOL fSelEnd, BYTE bFill, BYTE * rgbRcv, DWORD cbRcv, BOOL fOverlap);

/* ------------------------------------------------------------ */

#endif                    // DSPI_INCLUDED

/************************************************************************/
