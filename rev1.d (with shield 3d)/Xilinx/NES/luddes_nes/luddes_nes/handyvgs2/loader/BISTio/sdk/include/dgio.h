/************************************************************************/
/*                                                                      */
/*  dgio.h  --      Interface Declarations for DGIO.DLL                 */
/*                                                                      */
/************************************************************************/
/*  Author:     Gene Apperson                                           */
/*  Copyright 2009, Digilent Inc.                                       */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*  This header file contains the interface declarations for the API    */
/*  of the DGIO.DLL.  The DGIO DLL provides the implementation for the  */
/*  Digilent General Sensor and U/I Device interface. This interface is */
/*  used to access general purpose i/o devices that don't have a more   */
/*  specific interface.                                                 */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  06/24/2009(GeneA): created                                          */
/*  08/06/2009(GeneA): Added channel numbers to the interface.          */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  01/14/2009(GeneA): Added DgioGetConfigValue and DgioPutConfigValue  */
/*      functions. Added ival parameter to DgioGetData and DgioPutData  */
/*      functions.                                                      */
/*  02/25/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DGIO_INCLUDED)
#define      DGIO_INCLUDED

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

const int   chnGioMin   = 0;		//minimum possible valid channel number
const int   chnGioMax   = 7;		//maximum possible valid channel number

const int   cbGioDiscrete   = 4;    //size of a discrete value
const int   cbGioRanged     = 4;    //size of a ranged value

/* ------------------------------------------------------------ */
/*          GIO Port Properties Definitions                     */
/* ------------------------------------------------------------ */

/* Define the port property bits for DGIO ports.
*/
const DPRP dprpGioDiscreteIn    = 0x00000001;   // port provides discrete (bitwise) inputs
const DPRP dprpGioDiscreteOut   = 0x00000002;   // port provides discrete (bitwise) outputs
const DPRP dprpGioRangedIn      = 0x00000004;   // port provides ranged input
const DPRP dprpGioRangedOut     = 0x00000008;   // port provides ranged output
const DPRP dprpGioEncodedIn     = 0x00000010;   // port provides encoded input
const DPRP dprpGioEncodedOut    = 0x00000020;   // port provides encoded output
const DPRP dprpGioAbsolute      = 0x00000040;   // port supports absolute ranged in/out
const DPRP dprpGioRelative      = 0x00000080;   // port supports relative ranged in/out
const DPRP dprpGioTimeStamp     = 0x00000100;   // port supports time stamping data in

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
DPCAPI BOOL DgioGetVersion(char * szVersion);
DPCAPI BOOL DgioGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI BOOL DgioGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI BOOL DgioEnable(HIF hif);
DPCAPI BOOL DgioEnableEx(HIF hif, INT32 prtReq);
DPCAPI BOOL DgioDisable(HIF hif);

/* Port information and control functions
*/
DPCAPI BOOL DgioGetChanCount(HIF hif, INT32 * pcchn);
DPCAPI BOOL DgioGetChanProperties(HIF hif, INT32 chn, DWORD * pdprp);
DPCAPI BOOL DgioGetDiscreteMask(HIF hif, INT32 chn, DWORD * pdwMask);
DPCAPI BOOL DgioGetRangedCount(HIF hif, INT32 chn, INT32 * pcvalRng);
DPCAPI BOOL DgioInputEnable(HIF hif, INT32 chn);
DPCAPI BOOL DgioInputDisable(HIF hif, INT32 chn);
DPCAPI BOOL DgioOutputEnable(HIF hif, INT32 chn);
DPCAPI BOOL DgioOutputDisable(HIF hif, INT32 chn);
DPCAPI BOOL DgioPutConfigValue(HIF hif, INT32 chn, INT32 ival, DWORD dwVal);
DPCAPI BOOL DgioGetConfigValue(HIF hif, INT32 chn, INT32 ival, DWORD * pdwVal);

/* Data transfer functions
*/
DPCAPI BOOL DgioPutData(HIF hif, INT32 chn, INT32 ival, void * pvData, DWORD cbData, BOOL fOverlap);
DPCAPI BOOL DgioGetData(HIF hif, INT32 chn, INT32 ival, void * pvData, DWORD cbData, BOOL fOverlap);

/* ------------------------------------------------------------ */

#endif

/************************************************************************/
