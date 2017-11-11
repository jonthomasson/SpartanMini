/************************************************************************/
/*                                                                      */
/*  demc.h  --      Interface Declarations for DEMC.DLL                 */
/*                                                                      */
/************************************************************************/
/*  Author:     Gene Apperson                                           */
/*  Copyright 2009, Digilent Inc.                                       */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*  This header file contains the interface declarations for the API    */
/*  of the DEMC.DLL. This DLL provices API services for controlling     */
/*  various kinds of electro-mechanical actuators such as RC servos,    */
/*  brushed DC motors, stepper motors and so on.                        */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  06/05/2009(GeneA): created                                          */
/*  12/07/2009(GeneA): change int parameters to INT32                   */
/*  01/29/2010(GeneA): added support for stepper motor device classes   */
/*  02/25/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DEMC_INCLUDED)
#define      DEMC_INCLUDED

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

/* Define the port property bits for EMC ports.
*/
/* These bits define the device classes
*/
const DPRP dprpEmcRcServo       = 0x40000000;   // RC servo device class
const DPRP dprpEmcBrMotor       = 0x20000000;   // brushed DC motor device class
const DPRP dprpEmcBlMotor       = 0x10000000;   // brushless DC motor device class
const DPRP dprpEmcUniStep       = 0x08000000;   // uni-polar stepper motor device class
const DPRP dprpEmcBiStep        = 0x04000000;   // bi-polar stepper motor device class

/* These bit define class specific properties.
*/
const DPRP dprpEmcPos           = 0x00000001;   // port support setting position
const DPRP dprpEmcVel           = 0x00000002;   // port supports velocity control
const DPRP dprpEmcAccel         = 0x00000004;   // port supports acceleration control
const DPRP dprpEmcDecel         = 0x00000008;   // port supports deceleration control
const DPRP dprpEmcInvert        = 0x00000010;   // port supports position/direction inversion
const DPRP dprpEmcPersist       = 0x00000020;   // port supports saving parameters
const DPRP dprpEmcScript        = 0x00000040;   // port supports position scripting
const DPRP dprpEmcLoopControl   = 0x00000080;   // port supports closed loop motor speed control
const DPRP dprpEmcStepAbs       = 0x00000100;   // port supports absolute positioning
const DPRP dprpEmcStepRel       = 0x00000200;   // port supports relative positioning
const DPRP dprpEmcStepSubstep   = 0x00000400;   // port supports substepping

/* Properties related to the RC Servo device class.
*/
const INT32 chnSrvMin           = 0;            //minimum servo channel number
const INT32 chnSrvMax           = 31;           //maximum possible servo channel number

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
DPCAPI BOOL DemcGetVersion(char * szVersion);
DPCAPI BOOL DemcGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI BOOL DemcGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI BOOL DemcEnable(HIF hif);
DPCAPI BOOL DemcEnableEx(HIF hif, INT32 prtReq);
DPCAPI BOOL DemcDisable(HIF hif);

/* DEMC RC Servo Control Device Class
*/
DPCAPI BOOL DemcServoStoreSettings(HIF hif);
DPCAPI BOOL DemcServoLoadSettings(HIF hif);
DPCAPI BOOL	DemcServoGetChnCount(HIF hif, INT32 * pcchn);
DPCAPI BOOL DemcServoChnEnable(HIF hif, INT32 chn);
DPCAPI BOOL DemcServoChnDisable(HIF hif, INT32 chn);
DPCAPI BOOL DemcServoHalt(HIF hif, INT32 chn);
DPCAPI BOOL DemcServoHaltAll(HIF hif);
DPCAPI BOOL DemcServoSetPosAbs(HIF hif, INT32 chn, SHORT pos);
DPCAPI BOOL DemcServoSetPosRel(HIF hif, INT32 chn, SHORT rel);
DPCAPI BOOL DemcServoGetPos(HIF hif, INT32 chn, SHORT * ppos);
DPCAPI BOOL DemcServoGetMotion(HIF hif, DWORD * pdwMov);
DPCAPI BOOL DemcServoSetWidth(HIF hif, INT32 chn, USHORT tusWdt);
DPCAPI BOOL DemcServoGetWidth(HIF hif, INT32 chn, USHORT * ptusWdt);
DPCAPI BOOL DemcServoSetVel(HIF hif, INT32 chn, USHORT vel);
DPCAPI BOOL DemcServoGetVel(HIF hif, INT32 chn, USHORT * pvel);
DPCAPI BOOL DemcServoSetCenter(HIF hif, INT32 chn, USHORT tusCtr);
DPCAPI BOOL DemcServoGetCenter(HIF hif, INT32 chn, USHORT * ptusCtr);
DPCAPI BOOL DemcServoSetMin(HIF hif, INT32 chn, USHORT tusMin);
DPCAPI BOOL DemcServoGetMin(HIF hif, INT32 chn, USHORT * ptusMin);
DPCAPI BOOL DemcServoSetMax(HIF hif, INT32 chn, USHORT tusMax);
DPCAPI BOOL DemcServoGetMax(HIF hif, INT32 chn, USHORT * ptusMax);
DPCAPI BOOL DemcServoSetInvert(HIF hif, INT32 chn, BOOL fInvert);
DPCAPI BOOL DemcServoGetInvert(HIF hif, INT32 chn, BOOL * pfInvert);

/* DEMC Brushed DC Motor Device Class
*/
DPCAPI BOOL DemcBrdcSetVel(HIF hif, INT32 vel);
DPCAPI BOOL DemcBrdcGetVelSet(HIF hif, INT32 * pvel);
DPCAPI BOOL DemcBrdcGetVelCur(HIF hif, INT32 * pvel);
DPCAPI BOOL DemcBrdcGetPrdCur(HIF hif, DWORD * pprd);
DPCAPI BOOL DemcBrdcSetLoopEnable(HIF hif, BOOL fEnabled);
DPCAPI BOOL DemcBrdcGetLoopEnable(HIF hif, BOOL * pfEnabled);
DPCAPI BOOL DemcBrdcSetEncoderPeriod(HIF hif, double tsPrdMin, double tsPrdMax);
DPCAPI BOOL DemcBrdcSetLoopParam(HIF hif, double kp, double ki, double kd);
DPCAPI BOOL DemcBrdcSetLoopPeriod(HIF hif, double tsPeriod);

/* DEMC Stepper motor Device Class functions
*/
DPCAPI BOOL DemcStepSetRate(HIF hif, double stvReq, double * pstvSet);
DPCAPI BOOL DemcStepGetRate(HIF hif, double * pstvCur);
DPCAPI BOOL DemcStepSetAccel(HIF hif, double staReq, double * pstaSet);
DPCAPI BOOL DemcStepGetAccel(HIF hif, double * pstaCur);
DPCAPI BOOL DemcStepSetDecel(HIF hif, double staReq, double * pstaSet);
DPCAPI BOOL DemcStepGetDecel(HIF hif, double * pstaCur);
DPCAPI BOOL DemcStepMoveAbs(HIF hif, INT32 stpReq);
DPCAPI BOOL DemcStepMoveRel(HIF hif, INT32 stpReq);
DPCAPI BOOL DemcStepSetPos(HIF hif, INT32 stpReq);
DPCAPI BOOL DemcStepGetPos(HIF hif, INT32 * pstpCur);
DPCAPI BOOL DemcStepSetLimits(HIF hif, INT32 stpMax, INT32 stpMin);
DPCAPI BOOL DemcStepGetLimits(HIF hif, INT32 * pstpMaxCur, INT32 * pstpMinCur);
DPCAPI BOOL DemcStepSetSubstep(HIF hif, DWORD sbstReq, DWORD * psbsSet);
DPCAPI BOOL DemcStepGetSubstep(HIF hif, DWORD * psbstCur);
DPCAPI BOOL DemcStepGetMotion(HIF hif, BOOL * pfMov);
DPCAPI BOOL DemcStepHalt(HIF hif);

/* ------------------------------------------------------------ */

#endif

/************************************************************************/
