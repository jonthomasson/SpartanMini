`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    13:59:57 10/10/2017 
// Design Name: 
// Module Name:    blink 
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
module blink(
input wire clk,   // clock typically from 10MHz to 50MHz
output wire [7:0] led,
output wire ledtest
);
// create a binary counter
reg [31:0] cnt;
always @(posedge clk) cnt <= cnt+1;

assign ledtest = cnt[24];
assign led = 8'b00000000;
//assign led[0] = cnt[22];    // blink the LED at a few Hz (using the 23th bit of the counter, use a different bit to modify the blinking rate)
endmodule
