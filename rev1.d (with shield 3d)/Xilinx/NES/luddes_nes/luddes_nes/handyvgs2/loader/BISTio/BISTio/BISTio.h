/*
	BISTio Header File

	This file defines the interface into the BISTio Library
	Exports/Imports the classes and functions to interface with the BIST
*/

// Export Macro
// Ensure BISTIO_EXPORTS is not defined when using this in an application
#ifdef BISTIO_EXPORTS
	#define BISTIO_API __declspec(dllexport)
#else
	#define BISTIO_API __declspec(dllimport)
#endif

/* Typedefs That Are Required */
typedef unsigned short WORD;	// required in dpcdefs.h and we're not including windows.h by default
typedef unsigned long HIF;		// used so we don't have to make the client include dpcdecl.h
typedef unsigned char BYTE;		// another -_-
typedef int BOOL;

// Includes
#include "dpcdefs.h"			// defines several error message

/* Enumeration Declarations */
/**
	Enumerates the different Boundary Scan
	States

	This is used to denote which state the system is currently in
	or which state to move to
*/
enum BSState
{
	TEST_LOGIC_RESET	=	0, 
	RUN_IDLE			=	1,
	DR_SELECT			=	2,
	DR_CAPTURE			=	3,
	DR_SHIFT			=	4,
	DR_EXIT1			=	5,
	DR_EXIT2			=	6,
	DR_PAUSE			=	7,
	DR_UPDATE			=	8,
	IR_SELECT			=	9,
	IR_CAPTURE			=	10,
	IR_SHIFT			=	11,
	IR_EXIT1			=	12,
	IR_EXIT2			=	13,
	IR_PAUSE			=	14,
	IR_UPDATE			=	15,
};
/**
	Enumerates the different supported FPGA families
	for boundary scan

	This is used to denote the specific fpga that is connected when using boundary scan
	If none is specified when connecting, the default is the SPARTAN3.  Vertex causes it
	to treat the IR register as 10-bits.
*/
enum BSFPGA
{
	SPARTAN3,
	VERTEX
};
/**
	The device the system is connected to

	This will only work with Xilinx FPGAs which tell us the board ID 
*/
enum BSDevice
{
	dvcUnknown	=	0x0,
	dvcS1000	=	0x01428093,
	dvcS200		=	0x01414093
};
/**
	User to use for various operations

	These are used in the SetBSUser function when setting the IR register.
	In VERTEX mode, these are padded to make a 10-bit instruction.  Also User3
	and User4 are not valid in Spartan 3.
*/
enum BSInstruction
{
	// Test Modes
	EXTEST		=	0x00,		//000000
	SAMPLE		=	0x01,		//000001	
	INTEST		=	0x07,		//000111

	// Configuration Modes
	READBACK	=	0x04,		//000100
	CONFIGURE	=	0x05,		//000101

	// User Modes
	USER1		=	0x02,		//000010
	USER2		=	0x03,		//000011
	USER3		=	0x22,		//100010	(VERTEX Only)
	USER4		=	0x23,		//100011	(VERTEX Only)

	// Info Instructions
	IDCODE		=	0x08,		//001000
	USERCODE	=	0x09,		//001001

	// Other 
	BYPASS		=	0xFF,		//111111
};

/**
	This class is an abstract class which defines a basic interface for other classes to implement 
	It wraps a few of the basic functions of the Adept SDK
*/
class BISTIO_API BISTio
{
private:
	/*
		The handle to the open device if any
	*/
	HIF 				_hif;
public:
	/**
		Creates a new BISTio object
	*/
	BISTio();
	/**
		Handles clean up on destruction
		Will disconnect if connected
	*/
	~BISTio();
	/**
		Sets up the USB for the first use or
		Reconfigures it for talking with the programmer

		@returns false if mode is not set to USB
	*/
	bool ConfigureUSB();
	/**
		Returns the number of devices stored in the device table

		@returns -1 in case of error, otherwise number of devices
	*/
	int GetNumberOfDevices();

	/**
		Disconnects from the USB device if connected
		Ignored in parallel mode

		@returns false if already disconnected
	*/
	bool Disconnect();
	/**
		Connects to the USB device
		Ignored in parallel mode

		@returns false if unable to connect (will return true if already connected)
	*/
	bool Connect();
	/**
		Checks to see if this cable is already connected

		@returns true if connected
	*/
	bool IsConnected();

	/**
		Set the pins of the JTAG cable to a value

		@param tms	TMS pin
		@param tdi	TDI pin
		@param tck	TCK pin

		@returns true if successful
	*/
	bool SetPins(bool tms, bool tdi, bool tck);
	/**
		Returns the current values of tms, tdi, tdo, tck.
		The result is packed into the 4 LSBs of a BYTE. 

		@returns tms<<3|tdi<<2|tdo<<1|tck or 0xFF on failure
	*/
	BYTE GetPins();

	/**
		Clocks TCK for a specified number of clock cycles

		@param cycles	Number of clock cycles to clock tck for
		@param tms		Value to set tms to during clocks
		@param tdi		Value to set tdi to during clocks

		@returns true if successful
	*/
	bool ClockTck(unsigned long cycles, bool tdi, bool tms);
	/**
		Sends a given number of tdi bits into the the circuit
		Starting at the lsb of tdi[0] and going for the specified number of bits.

		The number of bytes in the tdi array (and tdo array if not NULL) 
		should be ceil(bits / 8)

		@param tdi			Byte array with the bits to set to tdi
		@param bits			number of bits in tdi
		@param tms			value to set tms to during shift operation
		@param tdo			Byte array to store tdo values (NULL if unused)
	*/
	bool SendTDIBits(BYTE *tdi, int bits, bool tms, BYTE *tdo = 0);
	/**
		Sends a given number of tms bits into the the circuit
		Starting at the lsb of tms[0] and going for the specified number of bits.

		The number of bytes in the tms array (and tdo array if not NULL) 
		should be ceil(bits / 8)

		@param tms			Byte array with the bits to set to tms
		@param bits			number of bits in tdi
		@param tdi			value to set tdi to during shift operation
		@param tdo			Byte array to store tdo values (NULL if unused)
	*/
	bool SendTMSBits(BYTE *tms, int bits, bool tdi, BYTE *tdo = 0);
	/**
		Sends a stream of TDI and TMS bits into the circuit
		The number of bits in tdi and tms must be the same

		@param tdi			Byte array with bits to set as tdi
		@param tms			Byte array with bits to set as tms
		@param bits			Number of bits to shift in 
		@param tdo			Byte array to store tdo values (NULL if unused)
	*/
	bool SendTDITMSBits(BYTE *tdi, BYTE *tms, int bits, BYTE *tdo = 0);
	/**
		Sets tdi and tms then retreives bits from tdo storing them in an array
		The bits retreived are stored in the lsb of tdo[0] first

		@param tdi			value of tdi
		@param tms			value of tms
		@param tdo			array to store tdo bits in 
		@param bits			number of bits to retreive

		@returns true if successful
	*/
	bool GetTDOBits(bool tdi, bool tms, BYTE *tdo, int bits);

	/**
		Returns the last error if any that occurred

		@returns Error Code
	*/
	static ERC GetLastError();
	/**
		Converts an ERC code into the symbolic name
		and description

		@param erc			Error Code
		@param szErrorName	Name of Error
		@param iNameLen		Length of szErrorName in characters
		@param szErrorDesc	Description of Error
		@param iDescLeng	Length of szErrorDesc in characters
	*/
	static BOOL StringFromERC(ERC erc, char *szErrorName, int iNameLength, char *szErrorDesc, int iDescLen);
	/**
		Reverse the bits in a byte array

		@param data			Byte Array 
		@param bits			Number of bits in array

		@returns the data array reversed
	*/
	static BYTE *ReverseBits(BYTE *data, int bits);
	/**
		Reverses a byte

		@param data		Byte to reverse
	*/
	static BYTE ReverseByte(BYTE data);
};

/**
	This class defines a boundary scan interface.  It is only guarenteed to work with Xilinx FPGAs
	though it is fairly generic and should work with other boundary scan interfaces with minor
	modifications
*/
class BISTIO_API BSio
	: public BISTio
{
private:
	/**
		Holds the current boundary scan state
	*/
	enum BSState _state;
	/**
		Holds the fpga family we're connected to
	*/
	enum BSFPGA	_family;

public:
	/**
		Connects to an FGPA using boundary scan

		@param family	Family of FPGA connecting to

		@returns True if successful
	*/
	bool Connect(enum BSFPGA family = SPARTAN3);
	/**
		Attempts to retrieve the board
		That the program is communicating with

		@returns The board being communicated with
	*/
	enum BSDevice GetDevice();
	/**
		Moves the device to a specified boundary scan state

		@attention Moving out of either shift state this way is not recommend since it will push an extra 0 into the shift register on exit.  The shift functions should be used to leave the shift state.

		@param bstate State to move boundary scan to
		
		@returns true if successful
	*/
	bool GotoBSState(enum BSState bstate);
	/**
		Returns the current boundary scan state

		@returns Current BS State
	*/
	enum BSState GetBSState();
	/**
		Sets the instruction in the IR register (commonly used for User mode selection)

		@param	user User to set

		@returns True if successful
	*/	
	bool SetBSInstruction(enum BSInstruction user);

	/**
		Shifts in a bit and returns tdo

		@param tdi		Bit to shift in
		@param tdo		Pointer to storage of output
		@param last		If last shift will finish shift mode

		@returns true if successful
	*/
	bool ShiftBit(bool tdi, bool *tdo = 0, bool last = false);
	/**
		Shifts in a character string of binary and returns tdo if requested

		The binary string should consist the numbers 1 and 0, "1010101"

		@param tdi		Character representation of binary string
		@param tdo		Pointer to the storage of the output, must be ceil(strlen(tdi)/8)
		@param last		If last shift will exit shift mode

		@returns true if successful
	*/
	bool ShiftBinary(const char *tdi, BYTE *tdo = 0, bool last = false);
	/**
		Shifts a byte of data in and returns tdo

		@param tdi		Byte to shift
		@param tdo		Pointer to the output byte should be length of 1
		@param last		If last shift will exit shift mode
		
		@returns true if successful
	*/
	bool ShiftByte(BYTE tdi, BYTE *tdo = 0, bool last = false);
	/**
		Shifts an array of bytes in and returns tdo

		@param tdi		Bytes to shift
		@param length	Length of byte array
		@param tdo		Optional output buffer
		@param last		If last shift will exit shift mode

		@returns true if successful
	*/
	bool ShiftBytes(BYTE *tdi, int length, BYTE *tdo = 0, bool last = false);

	/**
		Shifts a unsigned short in and returns two bytes of tdo

		@param tdi		Unsigned short to shift
		@param tdo		Optional output buffer (2 bytes)
		@param last		If last shift will exit shift mode

		@returns true if successful
	*/
	bool ShiftUShort(unsigned short tdi, BYTE *tdo = 0, bool last = false);
	/**
		Shifts a short in and returns two bytes of tdo

		@param tdi		Short to shift
		@param tdo		Optional output buffer (2 bytes)
		@param last		If last shift will exit shift mode

		@returns true if successful
	*/
	bool ShiftShort(short tdi, BYTE *tdo = 0, bool last = false);
	/**
		Shifts a unsigned integer in and returns four bytes of tdo

		@param tdi		Unsigned integer to shift
		@param tdo		Optional output buffer (4 bytes)
		@param last		If last shift will exit shift mode

		@returns true if successful
	*/
	bool ShiftUInt(unsigned int tdi, BYTE *tdo = 0, bool last = false);
	/**
		Shifts a integer in and returns four bytes of tdo

		@param tdi		integer to shift
		@param tdo		Optional output buffer (4 bytes)
		@param last		If last shift will exit shift mode

		@returns true if successful
	*/
	bool ShiftInt(int tdi, BYTE *tdo = 0, bool last = false);
}; 
