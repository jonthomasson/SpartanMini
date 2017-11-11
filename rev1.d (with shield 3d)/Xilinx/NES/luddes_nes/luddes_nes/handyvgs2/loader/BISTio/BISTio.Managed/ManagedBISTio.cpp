// This is the main DLL file.

// Include our managed wrapper class
#include "BISTio.Managed.h"

namespace ManagedBISTio
{
	ManagedBISTio::ManagedBISTio() { this->_bistio = new BISTio(); }
	ManagedBISTio::~ManagedBISTio() { delete this->_bistio; }
	bool ManagedBISTio::ConfigureUSB()
	{
		if (!_bistio->ConfigureUSB())
			return false;
		return true;
	}
	bool ManagedBISTio::Disconnect() { return this->_bistio->Disconnect(); }
	bool ManagedBISTio::Connect() { return this->_bistio->Connect(); }
	bool ManagedBISTio::IsConnected::get() { return this->_bistio->IsConnected(); }
	bool ManagedBISTio::SetPins(bool tms, bool tdi, bool tck) { return this->_bistio->SetPins(tms,tdi,tck); }
	Byte ManagedBISTio::GetPins() { return this->_bistio->GetPins(); }
	bool ManagedBISTio::ClockTck(unsigned long cycles, bool tdi, bool tms) { return this->_bistio->ClockTck(cycles,tdi,tms); }
	bool ManagedBISTio::SendTDIBits(array<Byte>^ tdi, int bits, bool tms, array<Byte>^ tdo)
	{
		pin_ptr<BYTE> p_tdi = &tdi[0];
		pin_ptr<BYTE> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bistio->SendTDIBits(p_tdi, bits, tms, p_tdo);
	}
	bool ManagedBISTio::SendTMSBits(array<Byte>^ tms, int bits, bool tdi, array<Byte>^ tdo)
	{
		pin_ptr<BYTE> p_tms = &tms[0];
		pin_ptr<BYTE> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bistio->SendTDIBits(p_tms, bits, tdi, p_tdo);
	}
	bool ManagedBISTio::SendTDITMSBits(array<Byte>^ tdi, array<Byte>^ tms, int bits, array<Byte>^ tdo)
	{
		pin_ptr<BYTE> p_tdi = &tdi[0];
		pin_ptr<BYTE> p_tms = &tms[0];
		pin_ptr<BYTE> p_tdo = nullptr;
		if (tdo != nullptr)
			p_tdo = &tdo[0];

		return this->_bistio->SendTDITMSBits(p_tdi, p_tms, bits, p_tdo);
	}

	bool ManagedBISTio::GetTDOBits(bool tdi, bool tms, array<Byte>^ tdo, int bits)
	{
		pin_ptr<BYTE> p_tdo = &tdo[0];
		return this->_bistio->GetTDOBits(tdi, tms, p_tdo, bits);
	}

	/* Static Functions */
	array<Byte>^ ManagedBISTio::ReverseBits(array<Byte>^ data, int bits)
	{
		pin_ptr<BYTE> p_data = &data[0];
		BISTio::ReverseBits(p_data,bits);
		return data;
	}
	Byte ManagedBISTio::ReverseByte(Byte data) { return BISTio::ReverseByte(data); }
	int ManagedBISTio::GetLastError() { return (int)BISTio::GetLastError(); }
	ERCError ManagedBISTio::GetErrorInfo(int error) 
	{
		char name[40];				// at the time of this writing the max is supposed to be 16
		char description[255];		// and 160, so there is some padding here

		if (BISTio::StringFromERC((ERC)error,name,40,description,255) <= 0)
			return ERCError();	// empty error struct

		String^ m_name = gcnew String(name);
		String^ m_desc = gcnew String(description);
		return ERCError(error,m_name,m_desc);
	}
}