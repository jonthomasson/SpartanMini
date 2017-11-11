using System;
using System.Text;
using System.Collections.Generic;
using System.Linq;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace BISTio.Managed.Tests
{
    /// <summary>
    /// Summary description for UnitTest1
    /// </summary>
    [TestClass]
    public class BasicTests
    {
        public BasicTests()
        {
            //
            // TODO: Add constructor logic here
            //
        }

        private TestContext testContextInstance;

        /// <summary>
        ///Gets or sets the test context which provides
        ///information about and functionality for the current test run.
        ///</summary>
        public TestContext TestContext
        {
            get
            {
                return testContextInstance;
            }
            set
            {
                testContextInstance = value;
            }
        }

        /// <summary>
        /// Object to communicate over boundary scan
        /// </summary>
        private static ManagedBISTio.ManagedBSio bs;

        #region Initialize and Cleanup
        [ClassInitialize]
        public static void TestInitialize(TestContext testContext) 
        {
            bs = new ManagedBISTio.ManagedBSio();
            bs.Connect(ManagedBISTio.FPGAFamily.SPARTAN3);
        }
        [ClassCleanup]
        public static void TestCleanup() 
        {
            bs.Disconnect();
            bs.Dispose();
        }
        #endregion

        [TestMethod]
        public void TestShiftBinary()
        {
            bs.SetBSInstruction(ManagedBISTio.Instruction.USER1);
            string data = "1111000011110000";
            bs.SetBSState(ManagedBISTio.State.DR_SHIFT);
            byte[] tdo = new byte[2];
            bs.ShiftBinary(data,false,tdo);

            // The result will be behind two bits so we just lose the last two bits sent and thats the result
            // So it should be 0011110000111100
            Assert.AreEqual<Byte>(tdo[0], 0x3C);
            Assert.AreEqual<Byte>(tdo[1], 0x3C);
        }

        [TestMethod]
        public void TestShiftBit()
        {
            // Get us in the right place
            bs.SetBSInstruction(ManagedBISTio.Instruction.USER1);
            bs.SetBSState(ManagedBISTio.State.DR_SHIFT);

            bool tdo = false;

            // The BS functions as a two-bit register so you have to two bits in before they start coming out
            bs.ShiftBit(true, false, ref tdo);
            bs.ShiftBit(true, false, ref tdo);

            // At this point we begin checking that the previously shifted in bit shows up on TDO
            bs.ShiftBit(false, false, ref tdo);
            Assert.IsTrue(tdo);

            bs.ShiftBit(true, false, ref tdo);
            Assert.IsTrue(tdo);

            bs.ShiftBit(false, false, ref tdo);
            Assert.IsFalse(tdo);
            bs.ShiftBit(true, false, ref tdo);
            Assert.IsTrue(tdo);
            bs.ShiftBit(false, false, ref tdo);
            Assert.IsFalse(tdo);
            bs.ShiftBit(true, false, ref tdo);
            Assert.IsTrue(tdo);
            bs.ShiftBit(false, false, ref tdo);
            Assert.IsFalse(tdo);
            bs.ShiftBit(true, false, ref tdo);
            Assert.IsTrue(tdo);
        }

        [TestMethod]
        public void TestReverseBytes()
        {
            Byte[] values = new Byte[] {
                0x10,
                0x42,
                0x08
            };
            Byte[] reversed = ManagedBISTio.ManagedBISTio.ReverseBits(values, 24);
            Assert.AreEqual(values, reversed);    // they should be the same object reference (not even just equal the same reference since its performed in place)
            Assert.AreEqual<Byte>(0x10, values[0]); // hilariously this array happens to be a palindrome... bad array for testing lol, will catch any issues on the 20 shift though
            Assert.AreEqual<Byte>(0x42, values[1]);
            Assert.AreEqual<Byte>(0x08, values[2]);
            ManagedBISTio.ManagedBISTio.ReverseBits(values, 24);
            Assert.AreEqual<Byte>(0x10, values[0]);
            Assert.AreEqual<Byte>(0x42, values[1]);
            Assert.AreEqual<Byte>(0x08, values[2]);

            ManagedBISTio.ManagedBISTio.ReverseBits(values, 20);
            Assert.AreEqual<Byte>(0x21,values[0],"First Byte Doesn't Match");
            Assert.AreEqual<Byte>(0x84,values[1],"Second Byte Doesn't Match");
            Assert.AreEqual<Byte>(0x00,values[2],"Third Byte Doesn't Match");
            ManagedBISTio.ManagedBISTio.ReverseBits(values, 20);
            Assert.AreEqual<Byte>(0x10,values[0],"First Byte Doesn't Match");
            Assert.AreEqual<Byte>(0x42,values[1],"Second Byte Doesn't Match");
            Assert.AreEqual<Byte>(0x08,values[2],"Third Byte Doesn't Match");
        }

        [TestMethod]
        public void TestReverseByte()
        {
            Byte value = 0x08;
            Byte reversed = ManagedBISTio.ManagedBISTio.ReverseByte(value);
            Assert.AreEqual<Byte>(0x10,reversed, "Reversed value is incorrect");
            Byte original = ManagedBISTio.ManagedBISTio.ReverseByte(reversed);
            Assert.AreEqual<Byte>(original, value, "Two Reverse Failed to be the same");
        }

        [TestMethod]
        public void TestError()
        {
            int error = ManagedBISTio.ManagedBISTio.GetLastError(); // should be 0 to indicate no error
            ManagedBISTio.ERCError info = ManagedBISTio.ManagedBISTio.GetErrorInfo(error);
            Assert.AreEqual(3072, info.Error);  // as long as no cable is connected
        }
    }
}
