// Copyright (c) 2012-2013 Ludvig Strigeus
// This program is GPL Licensed. See COPYING for the full license.

`timescale 1ns / 1ps

// Asynchronous PSRAM controller for byte access
// After outputting a byte to read, the result is available 70ns later.
module MemoryController(
                 input clk,
                 input read_a,             // Set to 1 to read from RAM
                 input read_b,             // Set to 1 to read from RAM
                 input write,              // Set to 1 to write to RAM
                 input [23:0] addr,        // Address to read / write
                 input [7:0] din,          // Data to write
                 output reg [7:0] dout_a,  // Last read data a
                 output reg [7:0] dout_b,  // Last read data b
                 output reg busy,          // 1 while an operation is in progress

                 output reg MemOE,         // Output Enable. Enable when Low.
                 output reg MemWR,         // Write Enable. WRITE when Low.
                 output MemAdv,            // Address valid. Keep LOW for Async.
                 output MemClk,            // Clock for sync oper. Keep LOW for Async.
                 output reg RamCS,         // Chip Enable. Active = LOW
                 output RamCRE,            // CRE = Control Register. LOW = Normal mode.
                 output reg RamUB,         // Upper byte enable
                 output reg RamLB,         // Lower byte enable
                 output reg [22:0] MemAdr,
                 inout [15:0] MemDB);
                 
  // These are always low for async operations
  assign MemAdv = 0;
  assign MemClk = 0;
  assign RamCRE = 0;
  reg [7:0] data_to_write;
  assign MemDB = MemOE ? {data_to_write, data_to_write} : 16'bz; // MemOE == 0 means we need to output tristate
  reg [1:0] cycles;
  reg r_read_a;
  
  always @(posedge clk) begin
    // Initiate read or write
    if (!busy) begin
      if (read_a || read_b || write) begin
        MemAdr <= addr[23:1];
        RamUB <= !(addr[0] != 0); // addr[0] == 0 asserts RamUB, active low.
        RamLB <= !(addr[0] == 0);
        RamCS <= 0;    // 0 means active
        MemWR <= !(write != 0); // Active Low
        MemOE <= !(write == 0);
        busy <= 1;
        data_to_write <= din;
        cycles <= 0;
        r_read_a <= read_a;
      end else begin
        MemOE <= 1;
        MemWR <= 1;
        RamCS <= 1;
        RamUB <= 1;
        RamLB <= 1;
        busy <= 0;
        cycles <= 0;
      end
    end else begin
      if (cycles == 2) begin
        // Now we have waited 3x45 = 135ns, latch incoming data on read.
        if (!MemOE) begin
          if (r_read_a) dout_a <= RamUB ? MemDB[7:0] : MemDB[15:8];
          else dout_b <= RamUB ? MemDB[7:0] : MemDB[15:8];
        end
        MemOE <= 1; // Deassert Output Enable.
        MemWR <= 1; // Deassert Write
        RamCS <= 1; // Deassert Chip Select
        RamUB <= 1; // Deassert upper/lower byte
        RamLB <= 1;
        busy <= 0;
        cycles <= 0;
      end else begin
        cycles <= cycles + 1;
      end
    end
  end
endmodule  // MemoryController

// Module reads bytes and writes to proper address in ram.
// Done is asserted when the whole game is loaded.
// This parses iNES headers too.
module GameLoader(input clk, input reset,
                  input [7:0] indata, input indata_clk,
                  output reg [21:0] mem_addr, output [7:0] mem_data, output mem_write,
                  output [31:0] mapper_flags,
                  output reg done,
                  output error);
  reg [1:0] state = 0;
  reg [7:0] prgsize;
  reg [3:0] ctr;
  reg [7:0] ines[0:15]; // 16 bytes of iNES header
  reg [21:0] bytes_left;
  
  assign error = (state == 3);
  wire [7:0] prgrom = ines[4];
  wire [7:0] chrrom = ines[5];
  assign mem_data = indata;
  assign mem_write = (bytes_left != 0) && (state == 1 || state == 2) && indata_clk;
  
  wire [2:0] prg_size = prgrom <= 1  ? 0 :
                        prgrom <= 2  ? 1 : 
                        prgrom <= 4  ? 2 : 
                        prgrom <= 8  ? 3 : 
                        prgrom <= 16 ? 4 : 
                        prgrom <= 32 ? 5 : 
                        prgrom <= 64 ? 6 : 7;
                        
  wire [2:0] chr_size = chrrom <= 1  ? 0 : 
                        chrrom <= 2  ? 1 : 
                        chrrom <= 4  ? 2 : 
                        chrrom <= 8  ? 3 : 
                        chrrom <= 16 ? 4 : 
                        chrrom <= 32 ? 5 : 
                        chrrom <= 64 ? 6 : 7;
  
  wire [7:0] mapper = {ines[7][7:4], ines[6][7:4]};
  wire has_chr_ram = (chrrom == 0);
  assign mapper_flags = {16'b0, has_chr_ram, ines[6][0], chr_size, prg_size, mapper};
  always @(posedge clk) begin
    if (reset) begin
      state <= 0;
      done <= 0;
      ctr <= 0;
      mem_addr <= 0;  // Address for PRG
    end else begin
      case(state)
      // Read 16 bytes of ines header
      0: if (indata_clk) begin
           ctr <= ctr + 1;
           ines[ctr] <= indata;
           bytes_left <= {prgrom, 14'b0};
           if (ctr == 4'b1111)
             state <= (ines[0] == 8'h4E) && (ines[1] == 8'h45) && (ines[2] == 8'h53) && (ines[3] == 8'h1A) && !ines[6][2] && !ines[6][3] ? 1 : 3;
         end
      1, 2: begin // Read the next |bytes_left| bytes into |mem_addr|
          if (bytes_left != 0) begin
            if (indata_clk) begin
              bytes_left <= bytes_left - 1;
              mem_addr <= mem_addr + 1;
            end
          end else if (state == 1) begin
            state <= 2;
            mem_addr <= 22'b10_0000_0000_0000_0000_0000; //{4'b0, 18'b10_0000_0000_0000_0000}; //22'b10_0000_0000_0000_0000_0000; // Address for CHR
            bytes_left <= {1'b0, chrrom, 13'b0};
          end else if (state == 2) begin
            done <= 1;
          end
        end
      endcase
    end
  end
endmodule


module NES_Nexys4(input CLK100MHZ,
                 input CPU_RESET,
                 input btnreset_nes,
                 input [7:0] SW,
					  input [7:0] joypad, //button array
					  input btn_menu,
					  input PROP_Tx, PROP_File_Tx,
                 output [7:0] LED,
                 //output [7:0] SSEG_CA,
                 //output [3:0] SSEG_AN,
                 // UART
                 input UART_RXD,
                 output UART_TXD,
					  output PROP_Rx, PROP_File_Rx,
                 // VGA
                 output vga_v, output vga_h, output [1:0] vga_r, output [1:0] vga_g, output [1:0] vga_b,
                 // Memory
                 output MemOE,          // Output Enable. Enable when Low.
                 output MemWR,          // Write Enable. WRITE when Low.
                 output MemAdv,         // Address valid. Keep LOW for Async.
                 input MemWait,         // Ignore for Async.
                 output MemClk,         // Clock for sync oper. Keep LOW for Async.
                 output RamCS,          // Chip Enable. Active = LOW
                 output RamCRE,         // CRE = Control Register. LOW = Normal mode.
                 output RamUB,          // Upper byte enable
                 output RamLB,          // Lower byte enable
                 output [18:0] MemAdr,
                 inout [15:0] MemDB,
                 // Sound board
                 output AUD_MCLK,
                 output AUD_LRCK,
                 output AUD_SCK,
                 output AUD_SDIN,
					  // audio
					  output AUDIO_L,
					  output AUDIO_R,
					  // TFT
                 output tft_v, output tft_h, output [3:0] tft_r, output [3:0] tft_g, output [3:0] tft_b, output tft_pclk, output tft_de, output tft_on
                 );

  wire clock_locked;
  wire clk;
  wire clk_25;
  wire clk_50;
  //clk_out1=21.477MHz system clock for ppu etc
  //clk_out2=25MHz clock for uart and loader.
  clk_wiz_v3_6 sys_clocks(.CLK_IN1(CLK100MHZ), .CLK_OUT1(), .CLK_OUT2(clk_50), .CLK_OUT3(clk), .RESET(1'b0), .LOCKED(clock_locked));

  assign sw = 8'b00000000;
  


		
  // UART
  wire [7:0] uart_data;
  wire [7:0] uart_addr;
  wire       uart_write;
  wire       uart_error;
  wire loader_reset;
	UartDemux uart_demux(.clk(clk),.reset(CPU_RESET), .uart_rx(PROP_File_Tx), .uart_tx(PROP_File_Rx), 
	.data(uart_data), .addr(uart_addr), .write(uart_write), .checksum_error(uart_error), .reset_loader(loader_reset));
  assign     UART_TXD = 1;
  
  
  // Loader
  wire [7:0] loader_input = uart_data;
  wire       loader_clk   = (uart_addr == 8'h37) && uart_write;
  reg  [7:0] loader_conf;
  reg  [7:0] loader_btn, loader_btn_2;
  always @(posedge clk) begin
    if (uart_addr == 8'h35 && uart_write)
      loader_conf <= uart_data;
//    if (uart_addr == 8'h40 && uart_write)
//      loader_btn <= uart_data;
    if (uart_addr == 8'h41 && uart_write)
      loader_btn_2 <= uart_data;
  end
  
  wire [7:0] joypad_deb, joypad_level;
  wire joypad_tick;
  //joypad button instantiation
  joypad_buttons buttons(.clk(clk), .joypad(joypad), .joypad_deb(joypad_deb), .joypad_level(joypad_level), .btn_strobe(joypad_tick));
	
  always @*
	begin
		if(joypad_tick)
			loader_btn = joypad_level;
	end

  // NES Palette -> RGB332 conversion
  reg [14:0] pallut[0:63];
  initial $readmemh("nes_palette.txt", pallut);

  // LED Display
  reg [31:0] led_value;
  reg [7:0] led_enable;
  //LedDriver led_driver(clk, led_value, led_enable, SSEG_CA, SSEG_AN);

  wire [8:0] cycle;
  wire [8:0] scanline;
  wire [15:0] sample;
  wire [5:0] color;
  wire joypad_strobe;
  wire [1:0] joypad_clock;
  wire [21:0] memory_addr;
  wire memory_read_cpu, memory_read_ppu;
  wire memory_write;
  wire [7:0] memory_din_cpu, memory_din_ppu;
  wire [7:0] memory_dout;
  reg [7:0] joypad_bits, joypad_bits2;
  reg [1:0] last_joypad_clock;
  wire [31:0] dbgadr;
  wire [1:0] dbgctr;

  reg [1:0] nes_ce;

  always @(posedge clk) begin
    if (joypad_strobe) begin
      joypad_bits <= loader_btn;
      joypad_bits2 <= loader_btn_2;
    end
    if (!joypad_clock[0] && last_joypad_clock[0])
      joypad_bits <= {1'b0, joypad_bits[7:1]};
    if (!joypad_clock[1] && last_joypad_clock[1])
      joypad_bits2 <= {1'b0, joypad_bits2[7:1]};
    last_joypad_clock <= joypad_clock;
  end
  
  wire [21:0] loader_addr;
  wire [7:0] loader_write_data;
//  wire loader_reset; //= loader_conf[0];
  wire loader_write;
  wire [31:0] mapper_flags;
  wire loader_done, loader_fail;
  GameLoader loader(clk, loader_reset, loader_input, loader_clk,
                    loader_addr, loader_write_data, loader_write,
                    mapper_flags, loader_done, loader_fail);

  wire reset_nes = (btnreset_nes || !loader_done);
  wire run_mem = (nes_ce == 0) && !reset_nes;
  wire run_nes = (nes_ce == 3) && !reset_nes;

  // NES is clocked at every 4th cycle.
  always @(posedge clk)
    nes_ce <= nes_ce + 1;
    
  NES nes(clk, reset_nes, run_nes,
          mapper_flags,
          sample, color,
          joypad_strobe, joypad_clock, {joypad_bits2[0], joypad_bits[0]},
          SW[4:0],
          memory_addr,
          memory_read_cpu, memory_din_cpu,
          memory_read_ppu, memory_din_ppu,
          memory_write, memory_dout,
          cycle, scanline,
          dbgadr,
          dbgctr);

  // This is the memory controller to access the board's PSRAM
  wire ram_busy;
  MemoryController memory(clk,
                          memory_read_cpu && run_mem, 
                          memory_read_ppu && run_mem,
                          memory_write && run_mem || loader_write,
                          loader_write ? {2'b00, loader_addr} : {2'b00, memory_addr},
                          loader_write ? loader_write_data : memory_dout,
                          memory_din_cpu,
                          memory_din_ppu,
                          ram_busy,
                          MemOE, MemWR, MemAdv, MemClk, RamCS, RamCRE, RamUB, RamLB, MemAdr, MemDB);
  reg ramfail;
  always @(posedge clk) begin
    if (loader_reset)
      ramfail <= 0;
    else
      ramfail <= ram_busy && loader_write || ramfail;
  end
  
  //menu toggle circuit
  reg toggle_menu;
  wire btn_menu_deb;
  
  //debounce for menu toggle button
  debounce deb_toggle_menu
      (.clk(clk), .reset(), .sw(btn_menu),
       .db_level(), .db_tick(btn_menu_deb));
		 
  always @(posedge clk, posedge CPU_RESET) begin
		if(CPU_RESET)
			toggle_menu = 1'b0;
		else
		if(btn_menu_deb)
			toggle_menu = !toggle_menu;
  end

//  wire [14:0] doubler_pixel;
//  wire doubler_sync;
//  wire [9:0] vga_hcounter, doubler_x;
//  wire [9:0] vga_vcounter;
  
//  VgaDriver vga(clk, vga_h, vga_v, vga_r, vga_g, vga_b, vga_hcounter, vga_vcounter, doubler_x, doubler_pixel, doubler_sync, SW[0]);
  //assign tft_clk = clk;
//  TftDriver tft(clk, tft_h, tft_v, tft_r, tft_g, tft_b, doubler_pixel, doubler_sync, SW[0], tft_clk);
	 Display display(.clk(clk), .reset(CPU_RESET), .reset_frame(scanline[8]), .reset_line((cycle[8:3] == 42)), 
			.hq2x_enable(SW[5]), .pixel(pallut[color]), .menu_toggle(toggle_menu), .joypad(joypad_deb[7:0]),
			.uart_Rx(PROP_Rx), .uart_Tx(PROP_Tx), .menu_clk(clk_50),
			.vga_h(vga_h), .vga_v(vga_v), .vga_r(vga_r), .vga_g(vga_g), .vga_b(vga_b),
			.tft_h(), .tft_v(), .tft_pclk(), .tft_de(), .tft_on(), .tft_r(), .tft_g(), .tft_b()
	 );
	 
//	 assign tft_on = SW[6];
//  wire [14:0] pixel_in = pallut[color];
//  Hq2x hq2x(clk, pixel_in, SW[5], 
//            scanline[8],        // reset_frame
//            (cycle[8:3] == 42), // reset_line
//            doubler_x,          // 0-511 for line 1, or 512-1023 for line 2.
//            doubler_sync,       // new frame has just started
//            doubler_pixel);     // pixel is outputted

  wire [15:0] sound_signal = {sample[15] ^ 1'b1, sample[14:0]};
//  wire [15:0] sound_signal_fir;
//  wire sample_now_fir;
//  FirFilter fir(clk, sound_signal, sound_signal_fir, sample_now_fir);
  // Display mapper info on screen
//  always @(posedge clk) begin
//    led_enable <= 255;
//    led_value <= sound_signal;
//  end
  always @(posedge clk) begin
    led_enable <= 255;
    led_value <= {uart_addr[7:0], uart_data[7:0]};
  end


assign AUDIO_R = audio;
assign AUDIO_L = audio;
wire audio;
sigma_delta_dac sigma_delta_dac (
	.DACout(audio),
	.DACin(sample[15:8]),
	.CLK(clk),
	.RESET(reset_nes)
);

//reg [7:0] sound_ctr;
//  always @(posedge clk)
//    sound_ctr <= sound_ctr + 1;
//  wire sound_load = /*SW[6] ? sample_now_fir : */(sound_ctr == 0);
//  SoundDriver sound_driver(clk, 
//      /*SW[6] ? sound_signal_fir : */sound_signal, 
//      sound_load,
//      sound_load,
//      AUD_MCLK, AUD_LRCK, AUD_SCK, AUD_SDIN);
 
  assign LED = {3'b0,toggle_menu, uart_error, ramfail, loader_fail, loader_done};
endmodule
