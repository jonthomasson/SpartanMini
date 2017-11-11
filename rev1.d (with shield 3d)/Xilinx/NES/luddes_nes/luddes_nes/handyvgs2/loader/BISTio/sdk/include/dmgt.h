/************************************************************************/
/*                                                                      */
/*    dmgt.h  --    Interface Declarations for  DMGT.DLL                */
/*                                                                      */
/************************************************************************/
/*    Author: Kovacs Laszlo Attila                                      */
/*    Copyright 2007 Digilent Inc.                                      */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*    This header file contains the interface declarations for the      */
/*    applications programming interface to the Digilent DMGT.DLL       */
/*                                                                      */
/*    This DLL provides API services to provide the management          */
/*    methods for Adept2.                                               */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  01/15/2008(KovacLA): Created                                        */
/*  01/12/2009(GeneA): Added power monitoring functions                 */
/*  02/25/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DMGT_INCLUDED)
#define      DMGT_INCLUDED

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

const MGTCAP mgtcapPowerOnOff   = 0x00000001;   //Device supports power on/off
const MGTCAP mgtcapConfigReset  = 0x00000002;   //Device supports config reset
const MGTCAP mgtcapUserReset    = 0x00000004;   //Device supports user reset
const MGTCAP mgtcapQueryDone    = 0x00000008;   //Device supports query done status
const MGTCAP mgtcapQueryPower   = 0x00000020;   //Device supports querying power state
const MGTCAP mgtcapMonitorPower = 0x00000040;   //Device support power supply monitoring

/* Power supply status values.
*/
const DWORD pwrMgtPowerOn       = 0x00000001;   //power supply is on
const DWORD pwrMgtVoltageFault  = 0x00000002;   //power supply voltage out of spec.
const DWORD pwrMgtCurrentFault  = 0x00000004;   //over current
const DWORD pwrMgtTempFault     = 0x00000008;   //over temperature fault

/* Maximum length of the power supply label string.
*/
const int   cchMgtPowerLabelMax = 32;

/* ------------------------------------------------------------ */
/*                  Object Class Declarations                   */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                  Variable Declarations                       */
/* ------------------------------------------------------------ */


/* ------------------------------------------------------------ */
/*                Interface Procedure Declarations              */
/* ------------------------------------------------------------ */

DPCAPI  BOOL    DmgtGetVersion(char * szVersion);

DPCAPI  BOOL    DmgtGetManagementCapabilities(HIF hif, MGTCAP * pmgtcap);
DPCAPI  BOOL    DmgtPowerSwitch(HIF hif, BOOL fOn);
DPCAPI  BOOL    DmgtQueryPowerState(HIF hif, BOOL * pfPowerCur);
DPCAPI  BOOL    DmgtConfigReset(HIF hif, BOOL fReset);
DPCAPI  BOOL    DmgtUserReset(HIF hif, BOOL fReset);
DPCAPI  BOOL    DmgtQueryDone(HIF hif, BOOL * pfState);

/* Power supply monitor facility
*/
DPCAPI BOOL     DmgtGetPowerSupplyCount(HIF hif, INT32 * pcnt);
DPCAPI BOOL     DmgtGetPowerSupplyData(HIF hif, INT32 idps, INT32 * pdwVlt, INT32 * pdwAmp, INT32 * pdwPwr, INT32 * pdwTmp, DWORD * pdwStatus);
DPCAPI BOOL     DmgtGetPowerSupplyProperties(HIF hif, INT32 idps, INT32 * pdwCnvVlt, INT32 * pdwCnvAmp, INT32 * pdwCnvPwr, INT32 * pdwCnvTmp);
DPCAPI BOOL     DmgtGetPowerSupplyLabel(HIF hif, INT32 chn, char * szLabel);

/* ------------------------------------------------------------ */

#endif                    // DMGT_INCLUDED

/************************************************************************/


