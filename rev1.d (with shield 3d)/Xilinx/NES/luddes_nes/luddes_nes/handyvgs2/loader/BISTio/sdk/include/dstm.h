/************************************************************************/
/*                                                                      */
/*    dstm.h    --    Interface Declarations for dstm.DLL               */
/*                                                                      */
/************************************************************************/
/*    Author: Joshua Pederson                                           */
/*    Copyright 2007 Digilent Inc.                                      */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    applications programming interface to the Digilent dstm.DLL       */
/*                                                                      */
/*    This DLL provides API services to provide the hi-speed            */
/*    synchronous data transfer application protocol for Adept2.        */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  04/23/2007(JPederson): Created                                      */
/*  08/15/2007(JPederson):  changed File and API name to dstm           */
/*  10/01/2008(GeneA): Added DstmEnableEx                               */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  02/26/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DSTM_INCLUDED)
#define      DSTM_INCLUDED

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


/* ------------------------------------------------------------ */
/*                  Object Class Declarations                   */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                  Variable Declarations                       */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                Interface Procedure Declarations                */
/* ------------------------------------------------------------ */

DPCAPI  BOOL    DstmGetVersion(char * szVersion);
DPCAPI  BOOL    DstmGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI  BOOL    DstmGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI  BOOL    DstmEnable(HIF hif);
DPCAPI  BOOL    DstmEnableEx(HIF hif, INT32 prtReq);
DPCAPI  BOOL    DstmDisable(HIF hif);

//overlapped functions
DPCAPI  BOOL    DstmIO (HIF hif, BYTE * rgbOut, DWORD cbOut, BYTE * rgbIn, DWORD cbIn, BOOL fOverlap);
DPCAPI  BOOL    DstmIOEx (HIF hif, BYTE * rgbOut, DWORD cbOut, BYTE * rgbIn, DWORD cbIn, BOOL fOverlap);

/* ------------------------------------------------------------ */

#endif                    // DSTM_INCLUDED

/************************************************************************/



