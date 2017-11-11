/************************************************************************/
/*                                                                      */
/*    depp.h  --    Interface Declarations for depp.DLL                 */
/*                                                                      */
/************************************************************************/
/*    Author: Joshua Pederson                                           */
/*    Copyright 2007 Digilent Inc.                                      */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    applications programming interface to the Digilent depp.DLL       */
/*                                                                      */
/*    This DLL provides API services to provide the EPP-style data      */
/*    transfer application protocol for Adept2.                         */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  04/23/2007(JPederson): Created                                      */
/*  08/15/2007(JPederson): changed File and API name to depp            */
/*  10/01/2008(GeneA): Added DeppEnableEx                               */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  02/25/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DEPP_INCLUDED)
#define      DEPP_INCLUDED


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

/* Define the port properties bits for EPP ports.
*/

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
/*                Interface Procedure Declarations              */
/* ------------------------------------------------------------ */

/* Basic interface functions.
*/
DPCAPI  BOOL    DeppGetVersion(char * szVersion);
DPCAPI  BOOL    DeppGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI  BOOL    DeppGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI  BOOL    DeppEnable(HIF hif);
DPCAPI  BOOL    DeppEnableEx(HIF hif, INT32 prtReq);
DPCAPI  BOOL    DeppDisable(HIF hif);

/* Data transfer functions
*/
DPCAPI  BOOL    DeppPutReg (HIF hif, BYTE bAddr, BYTE bData, BOOL fOverlap);
DPCAPI  BOOL    DeppGetReg (HIF hif, BYTE bAddr, BYTE * pbData, BOOL fOverlap);
DPCAPI  BOOL    DeppPutRegSet (HIF hif, BYTE * pbAddrData, DWORD nAddrDataPairs, BOOL fOverlap);
DPCAPI  BOOL    DeppGetRegSet (HIF hif, BYTE * pbAddr, BYTE * pbData, DWORD cbData, BOOL fOverlap);
DPCAPI  BOOL    DeppPutRegRepeat (HIF hif, BYTE bAddr, BYTE * pbData, DWORD cbData, BOOL fOverlap);
DPCAPI  BOOL    DeppGetRegRepeat (HIF hif, BYTE bAddr, BYTE * pbData, DWORD cbData, BOOL fOverlap);

/* Misc. control functions
*/
DPCAPI  BOOL    DeppSetTimeout(HIF hif, DWORD tnsTimeoutTry, DWORD * ptnsTimeout);

/* ------------------------------------------------------------ */

#endif                    // DEPP_INCLUDED

/************************************************************************/



