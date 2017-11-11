`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Jon Thomasson
// 
// Create Date:    06:37:25 12/08/2016 
// Design Name: 
// Module Name:    joypad_buttons 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: This module handles the debouncing of the joypad button array. It will
//						send the output array back in a format that can be directly input into
//						the NES.
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//						Incoming joypad array has following format:
//									0: BTN_A / 1: BTN_B / 2: BTN_SELECT / 3: BTN_START /
//									4: BTN_UP / 5: BTN_DOWN / 6: BTN_LEFT / 7: BTN_RIGHT
//////////////////////////////////////////////////////////////////////////////////
module joypad_buttons(
	input clk, reset,
	input [7:0] joypad, //joypad buttons
	output [7:0] joypad_deb, //debounced button array
	output [7:0] joypad_level,
	output reg btn_strobe //strobe to tell the nes when to read the button values
    );
	 
	wire btn_a, btn_b, btn_select, btn_start, 
		  btn_up, btn_down, btn_left, btn_right;
	wire btn_a_level, btn_b_level, btn_select_level, btn_start_level,
		  btn_up_level, btn_down_level, btn_left_level, btn_right_level;
	wire[7:0] joypad_deb_level;
	reg [7:0] joypad_reg, joypad_next;
	
		  
	// instantiate debounce circuit for the buttons
   debounce #(.N(21)) deb_unit1
      (.clk(clk), .reset(), .sw(joypad[0]),
       .db_level(btn_a_level), .db_tick(btn_a));
		 
   debounce #(.N(21)) deb_unit2
      (.clk(clk), .reset(), .sw(joypad[1]),
       .db_level(btn_b_level), .db_tick(btn_b));
		 
	debounce #(.N(21)) deb_unit3
      (.clk(clk), .reset(), .sw(joypad[2]),
       .db_level(btn_select_level), .db_tick(btn_select));
		 
	debounce #(.N(21)) deb_unit4
      (.clk(clk), .reset(), .sw(joypad[3]),
       .db_level(btn_start_level), .db_tick(btn_start));
		 
	debounce #(.N(21)) deb_unit5
      (.clk(clk), .reset(), .sw(joypad[4]),
       .db_level(btn_up_level), .db_tick(btn_up));
		 
	debounce #(.N(21)) deb_unit6
      (.clk(clk), .reset(), .sw(joypad[5]),
       .db_level(btn_down_level), .db_tick(btn_down));
		 
	debounce #(.N(21)) deb_unit7
      (.clk(clk), .reset(), .sw(joypad[6]),
       .db_level(btn_left_level), .db_tick(btn_left));
		 
	debounce #(.N(21)) deb_unit8
      (.clk(clk), .reset(), .sw(joypad[7]),
       .db_level(btn_right_level), .db_tick(btn_right));
		 
	assign joypad_deb = { btn_right,btn_left,btn_down,btn_up,btn_start,btn_select,btn_b,btn_a };
	assign joypad_deb_level = { btn_right_level,btn_left_level,btn_down_level,btn_up_level,btn_start_level,btn_select_level,btn_b_level,btn_a_level };
	assign joypad_level = joypad_deb_level;
	
	always @(posedge clk, posedge reset)
	begin
		if(reset)
		begin
			joypad_reg <= 8'h00;
		end
		else
		begin
			joypad_reg <= joypad_next;
		end
	end
	
	always @*
	begin
		joypad_next = joypad_deb_level;
		btn_strobe = 1'b0;
		
		if(joypad_next != joypad_reg)
			btn_strobe = 1'b1;
	end
endmodule
