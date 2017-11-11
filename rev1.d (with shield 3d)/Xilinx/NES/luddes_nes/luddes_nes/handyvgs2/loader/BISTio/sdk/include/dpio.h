/************************************************************************/
/*                                                                      */
/*    dpio.h  --    Interface Declarations for DPIO.DLL					*/
/*                                                                      */
/************************************************************************/
/*    Author: Joshua Pederson                                           */
/*    Copyright 2007 Digilent Inc.		                                */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    applications programming interface to the Digilent dpio.DLL		*/
/*                                                                      */
/*    This DLL provides API services to provide the PIO					*/
/*	  application protocol for Adept2.									*/
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*	04/23/2007(JPederson): Created										*/
/*	10/01/2008(GeneA): Added DpioEnableEx								*/
/*	12/07/2009(GeneA): change int parameters to INT32					*/
/*  02/26/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DPIO_INCLUDED)
#define      DPIO_INCLUDED

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
/*					Miscellaneous Declarations					*/
/* ------------------------------------------------------------ */

/* Define the port properties bits for PIO ports.
*/
const DPRP dprpPioDelay		= 0x00000001;	//device supports interbyte delay on stream i/o
const DPRP dprpPioStream	= 0x00000002;	//device supports PIO stream functions

/* ------------------------------------------------------------ */
/*					General Type Declarations					*/
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*					Object Class Declarations					*/
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*					Variable Declarations						*/
/* ------------------------------------------------------------ */

/* ------------------------------------------------------------ */
/*                Interface Procedure Declarations              */
/* ------------------------------------------------------------ */

DPCAPI  BOOL    DpioGetVersion(char * szVersion);
DPCAPI	BOOL	DpioGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI	BOOL	DpioGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI  BOOL    DpioEnable(HIF hif);
DPCAPI	BOOL	DpioEnableEx(HIF hif, INT32 prtReq);
DPCAPI  BOOL    DpioDisable(HIF hif);

DPCAPI	BOOL	DpioGetPinMask(HIF hif, DWORD * pfsMaskOut, DWORD * pfsMaskIn);
DPCAPI	BOOL	DpioGetPinDir(HIF hif, DWORD * pfsDir);
DPCAPI	BOOL	DpioSetPinDir(HIF hif, DWORD fsDirReq, DWORD * pfsDirSet);

DPCAPI	BOOL	DpioGetPinState(HIF hif, DWORD * pfsState);
DPCAPI	BOOL	DpioSetPinState(HIF hif, DWORD fsState);

DPCAPI  BOOL	DpioGetStreamTiming(HIF hif, DWORD * ptnsGetToSet, DWORD * ptnsSetToGet);
DPCAPI  BOOL	DpioSetStreamTiming(HIF hif, DWORD tnsGetToSet, DWORD tnsSetToGet, DWORD * ptnsGetToSet, DWORD * ptnsSetToGet);
DPCAPI	BOOL	DpioStreamState(HIF hif, BYTE *rgfsSet, BYTE * rgfsGet, DWORD cfs, BOOL * fHang, BOOL fOverlap);


/* ------------------------------------------------------------ */

#endif                    // dpio_INCLUDED

/************************************************************************/
