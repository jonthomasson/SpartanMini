
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Jon Thomasson
// 
// Create Date:    06:34:04 11/07/2016 
// Design Name: 
// Module Name:    display 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: Outer module for controlling various display adapters.
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module Display(
	input clk, reset, reset_frame, reset_line, hq2x_enable,
	input [14:0] pixel,        // Pixel for current cycle.
	input menu_toggle,
	input menu_clk,//50MHz clock for vga control of menu
	input [7:0] joypad,
	input uart_Tx, 
	output uart_Rx,
	//VGA
   output reg vga_h, output reg vga_v,
   output reg [1:0] vga_r, output reg[1:0] vga_g, output reg[1:0] vga_b,
	//TFT
	output reg tft_h, output reg tft_v, output reg tft_pclk, output reg tft_de, output reg tft_on,
	output reg [3:0] tft_r, output reg[3:0] tft_g, output reg[3:0] tft_b
   
    );

wire [14:0] pixel_doubled;
wire [9:0] next_pixel_x;
wire border = 1'b1;
wire sync;

// Horizontal and vertical counters
reg [9:0] h, v;
wire hpicture = (h < 512);                    // 512 lines of picture
wire hsync_on = (h == 512 + 23 + 35);         // HSync ON, 23+35 pixels front porch
wire hsync_off = (h == 512 + 23 + 35 + 82);   // Hsync off, 82 pixels sync
wire hend = (h == 681);                       // End of line, 682 pixels.

wire vpicture = (v < 480);                    // 480 lines of picture
wire vsync_on  = hsync_on && (v == 480 + 10); // Vsync ON, 10 lines front porch.
wire vsync_off = hsync_on && (v == 480 + 12); // Vsync OFF, 2 lines sync signal
wire vend = (v == 523);                       // End of picture, 524 lines. (Should really be 525 according to NTSC spec)
wire inpicture = hpicture && vpicture;

reg h_reg, v_reg;
reg [3:0] r_reg, g_reg, b_reg;

wire [9:0] new_h = (hend || sync) ? 0 : h + 1;
assign next_pixel_x = {sync ? 1'b0 : hend ? !v[0] : v[0], new_h[8:0]};



	Hq2x hq2x(.clk(clk), .inputpixel(pixel), .disable_hq2x(hq2x_enable), 
            .reset_frame(reset_frame),        // reset_frame
            .reset_line(reset_line), // reset_line
            .read_x(next_pixel_x),          // 0-511 for line 1, or 512-1023 for line 2.
            .frame_available(sync),       // new frame has just started
            .outpixel(pixel_doubled));     // pixel is outputted

always @(posedge clk) begin
  if(!menu_toggle)
  begin
  h <= new_h;
  if (sync) begin
    v_reg <= 1;
    h_reg <= 1;
    v <= 0;
  end else begin
    h_reg <= hsync_on ? 0 : hsync_off ? 1 : h_reg;
    if (hend)
      v <= vend ? 0 : v + 1;
    v_reg <= vsync_on ? 0 : vsync_off ? 1 : v_reg;
    r_reg <= pixel_doubled[4:1];
    g_reg <= pixel_doubled[9:6];
    b_reg <= pixel_doubled[14:11];
    if (border && (h == 0 || h == 511 || v == 0 || v == 479)) begin
      r_reg <= 4'b0000; //black border
      g_reg <= 4'b0000;
      b_reg <= 4'b0000;
    end
    if (!inpicture) begin
      r_reg <= 4'b0000;
      g_reg <= 4'b0000;
      b_reg <= 4'b0000;
    end
  end
  end //end if(!menu_toggle)
end

	// menu module
	wire rx_done;
	wire [7:0] rec_data;
	reg [7:0] send_data;
	reg txd_start;
	wire txd_busy;
	reg [2:0] rgb_reg;
	wire [2:0] rgb_next;
	wire[4:0] cursor_y;
	wire [9:0] pixel_x, pixel_y;
   wire video_on, pixel_tick;
	wire hsync, vsync;
	wire data_en;
	
   // instantiate main uart
	async_receiver#(.CLK_FREQ(25000000)) uart_receiver(.clk(clk), .RxD(uart_Tx), 
		.RxD_data_ready(rx_done), .RxD_data(rec_data));

	async_transmitter#(.CLK_FREQ(25000000)) uart_transmitter(.clk(clk), .TxD_start(txd_start), .TxD_data(send_data),
		.TxD(uart_Rx), .TxD_busy(txd_busy));
		
   // instantiate vga sync circuit
   video_sync
		#(.VID_HD(512)) vsync_unit
      (.clk(menu_clk), .reset(), .hsync(hsync), .vsync(vsync),
       .video_on(video_on), .p_tick(pixel_tick),
       .pixel_x(pixel_x), .pixel_y(pixel_y));
   // font generation circuit
   text_menu_gen text_gen_unit
      (.clk(clk), .video_on(video_on),
        .data(rec_data[7:0]), .data_en(data_en), .text_rx_done(rx_done), .pixel_x(pixel_x),
       .pixel_y(pixel_y), .cursor_y(cursor_y), .text_rgb(rgb_next), .move_up_tick(joypad[4]), 
		 .move_down_tick(joypad[5]), .btn_select(joypad[2]));
	
	//buttons output
	always @*
	begin
		txd_start = 1'b0;
		send_data = 8'h00;
		
		if(joypad[6] && menu_toggle) //left
		begin
			send_data = 8'h80;
			txd_start = 1'b1;
		end
		
		if(joypad[7] && menu_toggle) //right
		begin
			send_data = 8'h81;
			txd_start = 1'b1;
		end
		
		if(joypad[2] && menu_toggle && (cursor_y[4:0] != 5'b00000)) //select
		begin
			send_data = {3'b000, cursor_y[4:0]};
			txd_start = 1'b1;
		end
		
		if(joypad[0] && menu_toggle) //a
		begin
			send_data = 8'h83;
			txd_start = 1'b1;
		end
		
		if(joypad[1] && menu_toggle) //b
		begin
			send_data = 8'h82;
			txd_start = 1'b1;
		end
	end
	
	   // rgb buffer
	always @(posedge menu_clk)
	begin
		if (pixel_tick)
         rgb_reg <= rgb_next;
	end
	
	
	always @*
	begin
		if(menu_toggle)
		begin
			vga_h = hsync;
			vga_v = vsync;
			vga_r = rgb_reg[0] ? 4'b1111 : 4'b0000;
			vga_g = rgb_reg[1] ? 4'b1111 : 4'b0000;
			vga_b = rgb_reg[2] ? 4'b1111 : 4'b0000;
		end
		else
		begin
			vga_h = h_reg;
			vga_v = v_reg;
			vga_r = r_reg;
			vga_g = g_reg;
			vga_b = b_reg;
		end
	end
	
	
   // output
//   assign rgb = rgb_reg;
	assign data_en =  1'b1;
		
endmodule
