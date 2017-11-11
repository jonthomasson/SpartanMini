// Include our managed wrapper class
#include "BISTio.Managed.h"
#include <vcclr.h>
#include <stdlib.h>

namespace ManagedBISTio
{
	ManagedBSio::ManagedBSio() { this->_bsio = new BSio(); }
	ManagedBSio::~ManagedBSio() { delete this->_bsio; }

	bool ManagedBSio::Connect(FPGAFamily fpga) { return this->_bsio->Connect((BSFPGA)fpga); }
	bool ManagedBSio::Disconnect() { return this->_bsio->Disconnect(); }
	bool ManagedBSio::ConfigureUSB() { return this->_bsio->ConfigureUSB(); }
	bool ManagedBSio::IsConnected::get() { return this->_bsio->IsConnected(); }

	Device ManagedBSio::device::get() { return (Device)this->_bsio->GetDevice(); }
	State ManagedBSio::state::get() { return (State)this->_bsio->GetBSState(); }
	bool ManagedBSio::SetBSState(State state) { return this->_bsio->GotoBSState((BSState)state); }
	bool ManagedBSio::SetBSInstruction(Instruction instruction) 
	{ 
		return this->_bsio->SetBSInstruction((BSInstruction)instruction); 
	}
	bool ManagedBSio::ShiftBit(bool tdi, bool exit, bool% tdo)
	{
		pin_ptr<bool> p_tdo = &tdo;
		return this->_bsio->ShiftBit(tdi,p_tdo,exit);
	}
	bool ManagedBSio::ShiftBit(bool tdi, bool exit) { return this->_bsio->ShiftBit(tdi,NULL,exit); }
	bool ManagedBSio::ShiftBit(bool tdi) { return this->_bsio->ShiftBit(tdi,NULL,false); }
	bool ManagedBSio::ShiftBinary(String ^tdi, bool exit, array<Byte>^ tdo) 
	{
		// Converting from a string to wchar_t is easy.. char* a bit more complex
		pin_ptr<const wchar_t> wch = PtrToStringChars(tdi);
	    size_t convertedChars = 0;
	    char* cTDI = new char[tdi->Length+1];
	    wcstombs_s(&convertedChars, cTDI, tdi->Length+1, wch, _TRUNCATE);

		pin_ptr<BYTE> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];
		bool ret = this->_bsio->ShiftBinary(cTDI,p_tdo,exit);
		delete [] cTDI;
		return ret;
	}
	bool ManagedBSio::ShiftBinary(String ^tdi, bool exit) { return this->ShiftBinary(tdi,exit,nullptr); }
	bool ManagedBSio::ShiftBinary(String ^tdi) { return this->ShiftBinary(tdi,false,nullptr); }
	bool ManagedBSio::ShiftByte(BYTE tdi, bool exit, Byte% tdo) 
	{
		pin_ptr<BYTE> p_tdo = &tdo;
		return this->_bsio->ShiftByte(tdi,p_tdo,exit);
	}
	bool ManagedBSio::ShiftByte(BYTE tdi, bool exit) { return this->_bsio->ShiftByte(tdi,NULL,exit); }
	bool ManagedBSio::ShiftByte(BYTE tdi) { return this->_bsio->ShiftByte(tdi,NULL,false); }
	bool ManagedBSio::ShiftBytes(array<Byte>^ tdi, bool exit, array<Byte>^ tdo) 
	{
		if (tdi == nullptr)
			return false;

		pin_ptr<Byte> p_tdi = &tdi[0];
		pin_ptr<Byte> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bsio->ShiftBytes(p_tdi, tdi->Length, p_tdo,exit);
	}
	bool ManagedBSio::ShiftBytes(array<Byte>^ tdi, bool exit) { return this->ShiftBytes(tdi,exit,nullptr); }
	bool ManagedBSio::ShiftBytes(array<Byte>^ tdi) { return this->ShiftBytes(tdi,false,nullptr); }
	bool ManagedBSio::ShiftUShort(unsigned short tdi, bool exit, array<Byte>^ tdo) 
	{
		pin_ptr<Byte> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bsio->ShiftUShort(tdi,p_tdo,exit);
	}
	bool ManagedBSio::ShiftUShort(unsigned short tdi, bool exit) { return this->_bsio->ShiftUShort(tdi,NULL,exit); }
	bool ManagedBSio::ShiftUShort(unsigned short tdi) { return this->_bsio->ShiftUShort(tdi,NULL,false); }
	bool ManagedBSio::ShiftShort(short tdi, bool exit, array<Byte>^ tdo) 
	{
		pin_ptr<Byte> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bsio->ShiftShort(tdi,p_tdo,exit);
	}
	bool ManagedBSio::ShiftShort(short tdi, bool exit) { return this->_bsio->ShiftShort(tdi,NULL,exit); }
	bool ManagedBSio::ShiftShort(short tdi) { return this->_bsio->ShiftShort(tdi,NULL,false); }
	bool ManagedBSio::ShiftUInt(unsigned int tdi, bool exit, array<Byte>^ tdo) 
	{
		pin_ptr<Byte> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bsio->ShiftUInt(tdi,p_tdo,exit);
	}
	bool ManagedBSio::ShiftUInt(unsigned int tdi, bool exit) { return this->_bsio->ShiftUInt(tdi,NULL,exit); }
	bool ManagedBSio::ShiftUInt(unsigned int tdi) { return this->_bsio->ShiftUInt(tdi,NULL,false); }
	bool ManagedBSio::ShiftInt(int tdi, bool exit, array<Byte>^ tdo) 
	{
		pin_ptr<Byte> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bsio->ShiftInt(tdi,p_tdo,exit);
	}
	bool ManagedBSio::ShiftInt(int tdi, bool exit) { return this->_bsio->ShiftInt(tdi,NULL,exit); }
	bool ManagedBSio::ShiftInt(int tdi) { return this->_bsio->ShiftInt(tdi,NULL,false); }
}