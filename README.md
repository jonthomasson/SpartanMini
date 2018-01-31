
# SpartanMini
A flexible, simple, yet powerful FPGA development board.

As is the case with many things, the Spartan Mini was born out of a need I had when developing an FPGA project. I looked around at the development boards in the market, but I didn't see anything that met all of my requirements, so I decided to design one myself. There were many requirements for this board, which I will go into more detail about in the details section below, but my general requirements were as follows. I wanted a board I could hand solder fairly easily. This meant no bga. I wanted a board that was easy to program, containing both a JTAG port as well as USB. I wanted a board I could power with a wall wart and a barrel jack. The power needed to be switched. There needed to be plenty of GPIO, brought out to connectors that were preferably of a standardized format. I wanted some onboard RAM, preferrably SRAM or PSRAM for ease of use. Other than that I just wanted access to the bare metal of the FPGA, without a lot of fluff.

Continuing from the requirements stated in the description, here is a more in depth look at those requirements and how the Spartan Mini meets them:

1. A board that could be hand soldered fairly easily.

It seems like 90% or more of the FPGA's out there are in a BGA package. This made things difficult when considering this spec. I finally settled on the Spartan 6 FPGA because it came in a 144 pin TQFP package. The Spartan 6 is a well known and well supported FPGA among hackers and makers, making it a perfect candidate for the job.

2. A board that could be programmed easily with either JTAG or USB.

For the USB portion of this requirement, I decide to use the FT2232H chip by FTDI. This chip gave me both a USB to JTAG channel, as well as a USB to UART bridge that I could use later on to facilitate transferring data to the FPGA over the USB connection. I also wanted to include a full size 14 pin JTAG connector on board, to facilitate the use of a Xilinx Platform Cable USB programmer. This took a little more board space, but provides an easier interface to connect to the Xilinx programmer.

3. A board that could be powered with a wall wart and barrel jack.

This requirement was fairly simple to implement. The voltage requirements for the board fall between 3.7-6 volts dc. In addition to the barrel jack, the board provides jumpers to optionally be powered over USB, or a JST-PH connector and 3.7 volt lithium battery, as well as a voltage input pin.

4. The power needed to have a hard on/off switch.

Again, this requirement was not hard to implement. I just needed to select an adequate switch, capable of handling the current demands of the board.

5. No IO pin of the FPGA should be wasted. All pins should be brought out to standardized connectors on the edges of the board.

Many FPGA boards today seem like they waste a lot of IO on providing connectors on board that likely aren't needed by every project such as SD cards, VGA, HDMI, etc. Instead of using up the IO on peripherals that may be unneeded I opted to instead route all GPIO lines out to PMOD connectors. These connectors seem to be picking up in popularity and there are already tons of sensors/peripherals to choose from in the marketplace that can be plugged into the board if/when they're needed. In addition to the GPIO, I also wired GPIO pins to 8 user programmable LED's, 2 tactile buttons, and 1 slide switch. The addition of the 8 LED's aids greatly in debugging, but it also allows for precisely one byte of data to be represented in binary.

6. Access to onboard SRAM or PSRAM

This requirement is simply for the ease of use of SRAM over DRAM. The downside to SRAM is of course the price, which is why I settled on PSRAM instead. Essentially PSRAM provides an interface to the outside world that looks like SRAM, while internally it is made up of DRAM. As such, it is much cheaper than SRAM, but way less work to interface with than DRAM. This particular board provides 8Mb of PSRAM, which is adequate for my needs.

![enter image description here](https://lh3.googleusercontent.com/Ym8JBT1FlSJsortWRAH4dx5KHW2HkV1B4FOYHD6TUoF2Va7fMqjjbZRKk-YTAfOauaZ6iTyjpKmPpW8K9U_Lzy1sPvceVg2OTIK4zidJ0OYhVarUZ6AJo-_n0Bh1tX8kFqed3uyobCEtJzAthKT_NUfyR5vuuTG_k4TjL7J-cD8Y5W50PloVUXzOydISsuWan971t84IHQZvExRTL13VKr9Dzf7VFZQ4-1O7Eb2D59EVHCMWfp65vcO2BCi3f3q-bV_YtxEnLM_6e8DsP4a7GdczFiddMFkXQBkkdZaEMM2iFYc0Uvn_fpE_hW8l_2niM3Bjweu2Sg1JI46zMwf1BJlQvk6hKFwMn6nt-VLBW11oDaMBjqX9CXKMFm71dwxRTxzdKROl2nzPsxBll-ldlJ9pS-G4F2r8SEyl_1cLp4FI9L6Toqehjpdptvo6k-bQtzZX9d7uxOGFWja2dMNWYFRKiI2IBQzqyreGzzcMScAPFWFUQucwtIUtVOjU9eformU7DzSAqNybfNj_1Cf66kgaPlsM0UQ6a2LvAtUDOFYDCX_l58AIW41YAItvtlo8zSZ7KETyjbF2bbkrhY29mfstlfJ0lxFEip1irmiC=w1223-h688-no)

Here's a pic of the finished proto shield:
![enter image description here](https://lh3.googleusercontent.com/f9FaJq29ECEgaDPecJml5SKfVCc_7S3IVqZr0o6ec1YVCTRsc2OFJzyEswi_R8-aAgwqroxBXKtraHvqMPmY1geZjXxoQDiYGEtGb_RUlDSAVEsYpwZoTlxoZbM4P51sa-Vt0sLbR29HpZH1UwesNfGrU7usGoXFqWtqtPaZx9uNLdQ7OPx1LTOAEGCk1o-f30Efr-fSdV8IfqIKhRsLhNhf6uGuLrS2hRmcyPFA_5y_-zjL_bJP7FvzlHb9sfzDU2PzlZmgAsdUwXlsvXlLYDd9tAOhSbC9wxT-BG11320wBvbMLIENo6-fzY_uV0JjvE68gmNhEyKU-YtDyUu7bxQ82W3JjkRR4ERqWI5C3_PrNy0nRFSQO9gJaBm3a6roYfvGQnLvn1p-27fj_GhFGnUl9fpW3BOU36zx7_TFSxKjMyVTZvI7KFQ2qAHxUzBE4F75TqMSAB2Uwob8aPeds_ZgvLs6rGfP-yiNK4lMU7VbVyttNNkfqtt-WoIJwRs4Y94mybClMm4MMNdmQJFhci-No1nWAWSo5YfYCD34pjMW53zYsory0uwWILWmIv4T7k6NKAtzpBW4ahZvnReH060fJmjYZo16mgA0TTUV=w1223-h688-no)
