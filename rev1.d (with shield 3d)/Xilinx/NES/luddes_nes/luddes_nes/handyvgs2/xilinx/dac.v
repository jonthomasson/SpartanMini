`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    09:03:51 07/23/2016 
// Design Name: 
// Module Name:    dac 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module dac(DACout, DACin, Clk, Reset);
output DACout;
reg DACout;
input [`MSBI:0] DACin;
input Clk;
input Reset;

reg [`MSBI+2:0] DeltaAdder;
reg [`MSBI+2:0] SigmaAdder;
reg [`MSBI+2:0] SigmaLatch;
reg [`MSBI+2:0] DeltaB;

always @(SigmaLatch) DeltaB = {SigmaLatch[`MSBI+2], SigmaLatch[`MSBI+2]} << (`MSBI+1);
always @(DACin or DeltaB) DeltaAdder = DACin + DeltaB;
always @(DeltaAdder or SigmaLatch) SigmaAdder = DeltaAdder + SigmaLatch;
always @(posedge Clk or posedge Reset)
begin
    if(Reset)
    begin
        SigmaLatch <= #1 1'bl << (`MSBI+1);
        DACout <= #1 1'b0;
    end
    else
    begin
        SigmaLatch <== #1 SigmaAdder;
        DACout <= #1 SigmaLatch[`MSBI+2];
    end
end
endmodule
