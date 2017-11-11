// BISTio.Tests.cpp : Defines the entry point for the console application.
#include "stdafx.h"
#include <iostream>
#include "..\BISTio\BISTio.h"

#define TEST(x,y) if (x) { cout << "SUCCESS: " << y << endl; } else { cout << "FAIL: " << y << endl; PrintError(io.GetLastError()); }
#define TEST_NOIO(x,y) if (x) { cout << "SUCCESS: " << y << endl; } else { cout << "FAIL: " << y << endl; }

using namespace std;


void PrintError(ERC error);

int _tmain(int argc, _TCHAR* argv[])
{
	// Testing Reverse Functionality
	BYTE b[] = { 0xFF, 0x00, 0xF0 };
	BISTio::ReverseBits(b,24);
	TEST_NOIO(b[0] == 0x0F,"Reverse Bits Byte[0]");
	TEST_NOIO(b[1] == 0x00,"Reverse Bits Byte[1]");
	TEST_NOIO(b[2] == 0xFF,"Reverse Bits Byte[2]");
	BISTio::ReverseBits(b,24);
	TEST_NOIO(b[0] == 0xFF,"Reverse Bits 2 Byte[0]");
	TEST_NOIO(b[1] == 0x00,"Reverse Bits 2 Byte[1]");
	TEST_NOIO(b[2] == 0xF0,"Reverse Bits 2 Byte[2]");
	BYTE c[] = { 0x01, 0x24, 0x08 };
	BISTio::ReverseBits(c,20);		// reverse not on word boundary (only 20 bits)
	TEST_NOIO(c[0] == 0x41,"Reverse Bits 3 Byte[0]");
	TEST_NOIO(c[1] == 0x02,"Reverse Bits 3 Byte[1]");
	TEST_NOIO(c[2] == 0x08,"Reverse Bits 3 Byte[2]");
	BISTio::ReverseBits(c,20);		// reverse back not on word boundary (only 20 bits)
	TEST_NOIO(c[0] == 0x01,"Reverse Bits 4 Byte[0]");
	TEST_NOIO(c[1] == 0x24,"Reverse Bits 4 Byte[1]");
	TEST_NOIO(c[2] == 0x08,"Reverse Bits 4 Byte[2]");

	// Check BISTio
	BISTio io;
	TEST(io.Connect(),"CONNECT");
	TEST(io.Disconnect(),"DISCONNECT");

	BSio bs;
	TEST(bs.Connect(),"CONNECT")
	if (!bs.IsConnected())
		return -1;
	TEST(bs.SetBSInstruction(USER1),"SET INSTR")
	TEST(bs.GotoBSState(DR_SHIFT),"GOTO SHIFT")

	// Write Some SPI Words for Fun and Profit
	bs.ShiftBinary("0000000000000000000000001");
	BYTE btdo[10];
	memset(btdo,0,sizeof(BYTE)*10);
	bs.ShiftBinary("11000000000000000000000000000000000000001100000000000000000000001010011100",btdo);
	bs.ShiftBinary("000000000000000000000000000000000000",NULL,true);

	bs.GotoBSState(DR_SHIFT);
	bs.ShiftBinary("0000000000000000000000001");
	bs.ShiftBinary("00000000000000000000000001001000000000001000100000000001000000000010011100");
	bs.ShiftBinary("000000000000000000000000000000000000",NULL,true);

	TEST(bs.SetBSInstruction(USER2),"SET INSTR")
	TEST(bs.GotoBSState(DR_SHIFT),"GOTO SHIFT")
	bool booltdo = false;
	bs.ShiftBit(false,&booltdo,false);
	bs.ShiftBit(false,&booltdo,false);
	bs.ShiftBit(false,&booltdo,false);
	bs.ShiftBit(false,&booltdo,false);
	bs.ShiftBit(false,&booltdo,false);
	bs.ShiftBit(false,&booltdo,false);
	bs.ShiftBit(false,&booltdo,false);
	bs.ShiftBit(false,&booltdo,false);
	
	/*bs.GotoBSState(TEST_LOGIC_RESET);
	TEST(bs.SetBSInstruction(USER1),"SET INSTR")
	bs.GotoBSState(DR_SHIFT);
	BYTE tdo = 0;
	TEST(bs.ShiftBinary("0111",&tdo,true),"Shifted pattern")
	cout << tdo;

	tdo = 0;
	bs.GotoBSState(TEST_LOGIC_RESET);
	TEST(bs.SetBSInstruction(USER1),"SET INSTR")
	bs.GotoBSState(DR_SHIFT);
	bs.GetTDOBits(true,false,&tdo,8);
	cout << tdo;*/

	TEST(bs.Disconnect(),"DISCONNECT")

	return 0;
}

void PrintError(ERC error)
{
	char name[200];
	char description[200];
	memset(name,0,200);
	memset(description,0,200);

	BISTio::StringFromERC(error,name,200,description,200);

	cout << "FAILURE: " << name << endl;
	cout << "REASON: " << description << endl;
}

