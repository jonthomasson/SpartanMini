// BISTio.Managed.h
#pragma once

// Include Unmanaged Header
#include "..\BISTio\BISTio.h"

using namespace System;

namespace ManagedBISTio {
	public enum class Device
	{
		dvcUnknown	=	0x0,
		dvcS1000	=	0x01428093,
		dvcS200		=	0x01414093
	};
	public enum class Instruction
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
	public enum class FPGAFamily
	{
		SPARTAN3,
		VERTEX
	};
	public enum class State
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
		Declares an ERC Error structure
		That holds error information
	*/
	public value class ERCError 
	{
	private:
		int _error;
		String^ _name;
		String^ _desc;

	public:
		/**
			Returns the Error Code which occurred
		*/
		property int Error {
			int get() { return _error; }
		};
		/**
			Returns the name of the error which occurred
		*/
		property String^ Name {
			String^ get() { return _name; }
		};
		/**
			Returns the description of the error which occurred
		*/
		property String^ Description {
			String^ get() { return _desc; }
		};

		ERCError(int error, String^ name, String^ description)
		{
			_error = error;
			_name = name;
			_desc = description;
		}
	};

	public ref class ManagedBISTio
	{
	private:
		BISTio *_bistio;
	public:
		/**
			Creates a new BISTio object
		*/
		ManagedBISTio();
		/** 
			Destroys the BISTio object 
		*/
		~ManagedBISTio();

		// Properties
		/**
			Determines if device is connected
		*/
		property bool IsConnected { bool get(); }

		/**
			Sets up the USB for the first use or
			Reconfigures it for talking with the programmer

			@returns false if mode is not set to USB
		*/
		bool ConfigureUSB();
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
		Byte GetPins();

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
		bool SendTDIBits(array<Byte>^ tdi, int bits, bool tms, array<Byte>^ tdo);
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
		bool SendTMSBits(array<Byte>^ tms, int bits, bool tdi, array<Byte>^ tdo);
		/**
			Sends a stream of TDI and TMS bits into the circuit
			The number of bits in tdi and tms must be the same

			@param tdi			Byte array with bits to set as tdi
			@param tms			Byte array with bits to set as tms
			@param bits			Number of bits to shift in 
			@param tdo			Byte array to store tdo values (NULL if unused)
		*/
		bool SendTDITMSBits(array<Byte>^ tdi, array<Byte>^ tms, int bits, array<Byte>^ tdo);
		/**
			Sets tdi and tms then retreives bits from tdo storing them in an array
			The bits retreived are stored in the lsb of tdo[0] first

			@param tdi			value of tdi
			@param tms			value of tms
			@param tdo			array to store tdo bits in 
			@param bits			number of bits to retreive

			@returns true if successful
		*/
		bool GetTDOBits(bool tdi, bool tms, array<Byte>^ tdo, int bits);

		/**
			Returns the last error code which occurred if any

			@returns 0 if no error has occurred, otherwise the error code
		*/
		static int GetLastError();
		/**
			Returns the information about an error including name
			and description

			@returns Error Information Struct
		*/
		static ERCError GetErrorInfo(int error);

		/**
			Reverse the bits in a byte array, performed in place

			@param data			Array to reverse
			@param bits			Number of bits in array

			@returns the data array reversed. Operates in place!
		*/
		static array<Byte>^ ReverseBits(array<Byte>^ data, int bits);
		/**
			Reverses a byte, performed in place

			@param data		Byte to reverse

			@returns the reversed byte
		*/
		static Byte ReverseByte(Byte data);
	};

	public ref class ManagedBSio
	{
	public:
		/**
			Creates a Managed BSio Object
		*/
		ManagedBSio();
		/**
			Destroys the Managed BSio Object
		*/
		~ManagedBSio();

		/**
			Connects to an FGPA using boundary scan

			@param family	Family of FPGA connecting to

			@returns True if successful
		*/
		bool Connect(FPGAFamily family);
		/**
			Disconnect from Device
		*/
		bool Disconnect();

		/**
			Returns the currently connected device
		*/
		property Device device {
			Device get();
		}
		/**
			Returns the current boundary scan state
		*/
		property State state  {
			State get();
		}
		/**
			Returns if the cable is connected
		*/
		property bool IsConnected {
			bool get();
		}

		/**
			Moves to the given boundary scan
			register

			@param state The BS State to move to

			@warning If in the SHIFT state a 1 will be shifted in upon exit!
		*/
		bool SetBSState(State state);

		/**
			Sets the instruction in the IR register (commonly used for User mode selection)

			@param	user User to set

			@returns True if successful
		*/	
		bool SetBSInstruction(Instruction user);
		/**
			Configures the USB interface
		*/
		bool ConfigureUSB();

		/**
			Shifts in a bit and returns tdo

			@param tdi		Bit to shift in
			@param tdo		Pointer to storage of output
			@param last		If last shift will finish shift mode

			@returns true if successful
		*/
		bool ShiftBit(bool tdi, bool exit, bool% tdo);
		bool ShiftBit(bool tdi, bool exit);
		bool ShiftBit(bool tdi);
		/**
			Shifts in a character string of binary and returns tdo if requested

			The binary string should consist the numbers 1 and 0, "1010101"

			@param tdi		Character representation of binary string
			@param tdo		Pointer to the storage of the output, must be ceil(strlen(tdi)/8)
			@param last		If last shift will exit shift mode

			@returns true if successful
		*/
		bool ShiftBinary(String^ tdi, bool exit, array<Byte>^ tdo);
		bool ShiftBinary(String^ tdi, bool exit);
		bool ShiftBinary(String^ tdi);
		/**
			Shifts a byte of data in and returns tdo

			@param tdi		Byte to shift
			@param tdo		Pointer to the output byte should be length of 1
			@param last		If last shift will exit shift mode
			
			@returns true if successful
		*/
		bool ShiftByte(Byte tdi, bool exit, Byte% tdo);
		bool ShiftByte(Byte tdi, bool exit);
		bool ShiftByte(Byte tdi);
		/**
			Shifts an array of bytes in and returns tdo

			@param tdi		Bytes to shift
			@param length	Length of byte array
			@param tdo		Optional output buffer
			@param last		If last shift will exit shift mode

			@returns true if successful
		*/
		bool ShiftBytes(array<Byte>^ tdi, bool exit, array<Byte>^ tdo);
		bool ShiftBytes(array<Byte>^ tdi, bool exit);
		bool ShiftBytes(array<Byte>^ tdi);
		/**
			Shifts a unsigned short in and returns two bytes of tdo

			@param tdi		Unsigned short to shift
			@param tdo		Optional output buffer (2 bytes)
			@param last		If last shift will exit shift mode

			@returns true if successful
		*/
		bool ShiftUShort(unsigned short tdi, bool exit, array<Byte>^ tdo);
		bool ShiftUShort(unsigned short tdi, bool exit);
		bool ShiftUShort(unsigned short tdi);
		/**
			Shifts a short in and returns two bytes of tdo

			@param tdi		Short to shift
			@param tdo		Optional output buffer (2 bytes)
			@param last		If last shift will exit shift mode

			@returns true if successful
		*/
		bool ShiftShort(short tdi, bool exit, array<Byte>^ tdo);
		bool ShiftShort(short tdi, bool exit);
		bool ShiftShort(short tdi);
		/**
			Shifts a unsigned integer in and returns four bytes of tdo

			@param tdi		Unsigned integer to shift
			@param tdo		Optional output buffer (4 bytes)
			@param last		If last shift will exit shift mode

			@returns true if successful
		*/
		bool ShiftUInt(unsigned int tdi, bool exit, array<Byte>^ tdo);
		bool ShiftUInt(unsigned int tdi, bool exit);
		bool ShiftUInt(unsigned int tdi);
		/**
			Shifts a integer in and returns four bytes of tdo

			@param tdi		integer to shift
			@param tdo		Optional output buffer (4 bytes)
			@param last		If last shift will exit shift mode

			@returns true if successful
		*/
		bool ShiftInt(int tdi, bool exit, array<Byte>^ tdo);
		bool ShiftInt(int tdi, bool exit);
		bool ShiftInt(int tdi);

		private:
			BSio *_bsio;
	}; 
}
