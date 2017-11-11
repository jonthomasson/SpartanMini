/************************************************************************/
/*                                                                      */
/*  daio.h  --      Interface Declarations for DAIO.DLL                 */
/*                                                                      */
/************************************************************************/
/*  Author:     Gene Apperson                                           */
/*  Copyright 2009, Digilent Inc.                                       */
/************************************************************************/
/*  File Description:                                                   */
/*                                                                      */
/*  This header file contains the interface declarations for the API    */
/*  of the DAIO.DLL. This DLL provides API services for analog input/   */
/*  output ports.                                                       */
/*                                                                      */
/************************************************************************/
/*  Revision History:                                                   */
/*                                                                      */
/*  06/24/2009(GeneA): created                                          */
/*  02/25/2010(MichaelA): rewrote to be cross platform compatible       */
/*                                                                      */
/************************************************************************/

#if !defined(DAIO_INCLUDED)
#define      DAIO_INCLUDED

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

const INT32 chnAioMin   = 0;
const INT32 chnAioMax   = 31;       //maximum possible valid channel number

/* ------------------------------------------------------------ */
/*          EMC Port Properties Definitions                     */
/* ------------------------------------------------------------ */

/* Define the port property bits for ACI ports.
*/
const DPRP dprpAioInput         = 0x00000001;   // port provides analog inputs
const DPRP dprpAioOutput        = 0x00000002;   // port provides analog outputs
const DPRP dprpAioSingle        = 0x00000004;   // port supports single sample mode
const DPRP dprpAioContinuous    = 0x00000008;   // port supports continuous sampling
const DPRP dprpAioOneShot       = 0x00000010;   // port supports one shot operation
const DPRP dprpAioWaveOut       = 0x00000020;   // port supports wave table output
const DPRP dprpAioFifo          = 0x00000040;   // port supports fifo mode for continuous sampling
const DPRP dprpAioBuffered      = 0x00000080;   // port supports buffered mode for continuous sampling
const DPRP dprpAioSetRate       = 0x00000100;   // port supports setting sample rate
const DPRP dprpAioSetFormat     = 0x00000200;   // port supports setting sample size
const DPRP dprpAioSetGain       = 0x00000400;   // port supports setting channel gains
const DPRP dprpAioSetOffset     = 0x00000800;   // port supports setting channel DC offset
const DPRP dprpAioSetLow        = 0x00001000;   // port supports setting low pass filter cutoff
const DPRP dprpAioSetHigh       = 0x00002000;   // port supports setting high pass filter cutoff
const DPRP dprpAioSetRef        = 0x00004000;   // port supports setting the converter reference
const DPRP dprpAioExtRef        = 0x00008000;   // port supports external voltage reference

/* Define sampling mode format bits.
*/
const DWORD sprpAioSmpLeft      = 0x00000001;   // bits are left justified in sample
const DWORD sprpAioSmpRight     = 0x00000002;   // bits are right justified in sample
const DWORD sprpAioSmpUnsigned  = 0x00000004;   // samples are unsigned binary
const DWORD sprpAioSmpSigned    = 0x00000008;   // samples are unsigned twos-complement
const DWORD sprpAioSmpPacked    = 0x00000010;   // samples are packed in the buffer

/* Define buffer mode style bits.
*/
const DWORD bfmdAioFifo         = 0x00000001;   // select FIFO mode
const DWORD bfmdAioBuffered     = 0x00000002;   // select BUFFERED mode
const DWORD bfmdAioWait         = 0x00000100;   // wait when buffer full/empty
const DWORD bfmdAioFail         = 0x00000200;   // fail i/o operation when buffer is full/empty

/* Sampling modes for the converter associated with an AIO port.
*/
const DWORD smdAioSingle        = 0;            // port is in single sample mode
const DWORD smdAioContinuous    = 1;            // port is in continuous sample mode

/* Run modes for the DaioSetRun function.
*/
const DWORD rmdAioStop          = 0;            // stop sampling
const DWORD rmdAioRun           = 1;            // start sampling
const DWORD	rmdAioRunSingle		= 2;			// start single capture sampling
const DWORD rmdAioArm           = 3;            // wait for trigger
const DWORD	rmdAioArmSingle		= 4;			// wait for trigger for single capture sampling

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
DPCAPI BOOL DaioGetVersion(char * szVersion);
DPCAPI BOOL DaioGetPortCount(HIF hif, INT32 * pcprt);
DPCAPI BOOL DaioGetPortProperties(HIF hif, INT32 prtReq, DWORD * pdprp); 
DPCAPI BOOL DaioEnable(HIF hif);
DPCAPI BOOL DaioEnableEx(HIF hif, INT32 prtReq);
DPCAPI BOOL DaioDisable(HIF hif);

/* Sample I/O Functions
*/
DPCAPI BOOL DaioGetSample(HIF hif, INT32 chn, INT32 * psmp);
DPCAPI BOOL DaioPutSample(HIF hif, INT32 chn, INT32 smp);
DPCAPI BOOL DaioGetBuffer(HIF hif, INT32 chn, DWORD cbRcv, void * rgbRcv, BOOL fOverlap);
DPCAPI BOOL DaioPutBuffer(HIF hif, INT32 chn, DWORD cbSnd, void * rgbSnd, BOOL fOverlap);

/* Control and status functions.
*/
DPCAPI BOOL DaioGetChannelCount(HIF hif, INT32 * pchnCnt);
DPCAPI BOOL DaioChannelEnable(HIF hif, INT32 chn);
DPCAPI BOOL DaioChannelDisable(HIF hif, INT32 chn);
DPCAPI BOOL DaioGetReference(HIF hif, double * pvltCur);
DPCAPI BOOL DaioSetReference(HIF hif, double vltReq, double * pvltSet);
DPCAPI BOOL DaioSetSampleRate(HIF hif, double pfrqReq, double * pfrqSet);
DPCAPI BOOL DaioGetSampleRate(HIF hif, double * pfrqCur);
DPCAPI BOOL DaioGetLowCutoff(HIF hif, INT32 chn, double * pfrqCur);
DPCAPI BOOL DaioSetLowCutoff(HIF hif, INT32 chn, double frqReq, double * pfrqSet);
DPCAPI BOOL DaioGetHighCutoff(HIF hif, INT32 chn, double * pfrqCur);
DPCAPI BOOL DaioSetHighCutoff(HIF hif, INT32 chn, double frqReq, double * pfrqSet);
DPCAPI BOOL DaioGetGain(HIF hif, INT32 chn, double * pcgnCur);
DPCAPI BOOL DaioSetGain(HIF hif, INT32 chn, double cgnReq, double * pcgnSet);
DPCAPI BOOL DaioGetOffset(HIF hif, INT32 chn, double * pvltCur);
DPCAPI BOOL DaioSetOffset(HIF hif, INT32 chn, double vtlReq, double * pvltSet);
DPCAPI BOOL DaioSetPortMode(HIF hif, DWORD smdMode);
DPCAPI BOOL DaioGetRunMode(HIF hif, DWORD * prmdCur);
DPCAPI BOOL DaioSetRunMode(HIF hif, DWORD rmdRun);
DPCAPI BOOL DaioSetChannelMode(HIF hif, INT32 chn, DWORD dprpChmd);
DPCAPI BOOL DaioGetBufferInfo(HIF hif, INT32 chn, INT32 * pcbufMax, INT32 * pcbMax, INT32 * pcbBuf);
DPCAPI BOOL DaioSetBufferMode(HIF hif, INT32 chn, DWORD bfmdReq, DWORD * pbfmdSet, INT32 cbufReq, INT32 * pcbufSet);
DPCAPI BOOL DaioGetSampleFormat(HIF, INT32 * pcbtSmp, INT32 * pcbtSig, DWORD * psprpFmt);

/* ------------------------------------------------------------ */

#endif

/************************************************************************/
