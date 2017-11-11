// Copyright (c) 2012-2013 Ludvig Strigeus
// This program is GPL Licensed. See COPYING for the full license.

//module Rs232Tx(input clk, output UART_TX, input [7:0] data, input send, output reg uart_ovf, output reg sending);
//  reg [9:0] sendbuf = 9'b000000001;
//  //reg sending;
//  reg [13:0] timeout;
//  assign UART_TX = sendbuf[0];
// 
//  always @(posedge clk) begin
//    if (send && sending)
//      uart_ovf <= 1;
//  
//    if (send && !sending) begin
//      sendbuf <= {1'b1, data, 1'b0};
//      sending <= 1;
//      timeout <= 100 - 1; // 115200
//    end else begin
//      timeout <= timeout - 1;
//    end
//    
//    if (sending && timeout == 0) begin
//      timeout <= 100 - 1; // 115200
//      if (sendbuf[8:0] == 9'b000000001)
//        sending <= 0;
//      else
//        sendbuf <= {1'b0, sendbuf[9:1]};
//    end
//  end
//endmodule
//
//module Rs232Rx(input clk, input UART_RX, output [7:0] data, output send);
//  reg [8:0] recvbuf;
//  reg [5:0] timeout = 10/2 - 1;
//  reg recving;
//  reg data_valid = 0;
//  assign data = recvbuf[7:0];
//  assign send = data_valid;
//  always @(posedge clk) begin
//    data_valid <= 0;
//    timeout <= timeout - 6'd1;
//    if (timeout == 0) begin
//      timeout <= 10 - 1;
//      recvbuf <= (recving ? {UART_RX, recvbuf[8:1]} : 9'b100000000);
//      recving <= 1;
//      if (recving && recvbuf[0]) begin
//        recving <= 0;
//        data_valid <= UART_RX;
//      end
//    end
//    // Once we see a start bit we want to wait
//    // another half period for it to become stable.
//    if (!recving && UART_RX)
//      timeout <= 10/2 - 1;
//  end
//endmodule

// Decodes incoming UART signals and demuxes them into addr/data lines.
// This is a simple state machine which translates the checksum, count, address, and data for each packet sent from the pc.
// Packet Format: 
//   1 byte checksum | 1 byte address | 1 byte count | (count + 1) data bytes
module UartDemux(
	input clk, input reset, input uart_rx, 
	output uart_tx, output [7:0] data, 
	output [7:0] addr, output write, 
	output checksum_error, output reg reset_loader
	);
	
	// symbolic state declaration
   localparam  [3:0]
               idle  = 4'b0000,
					idle2 = 4'b0001,
               numpackets1 = 4'b0010,
               numpackets2 = 4'b0011,
					numpackets3 = 4'b0100,
					load = 4'b0101,  
					load2 = 4'b0110,
					load3 = 4'b0111,
					done = 4'b1000;
					
 // signal declaration
   reg [3:0] state_reg, state_next;
   wire rxfx_done;
   wire [7:0] recfx_data;
	reg [7:0] sendfx_data;
	reg txdfx_start;
	wire txdfx_busy;
	wire success_tick, error_tick;
	reg [15:0] num_packets;
	//reg reset_loader;
	wire demux_en;
	wire [7:0] demux_state, demux_count;
	reg [15:0] num_packets_reg, num_packets_next;
	reg done_tick;
	
	
//body
	// instantiate file transfer uart
	async_receiver uart_receiverfx(.clk(clk), .RxD(uart_rx), 
		.RxD_data_ready(rxfx_done), .RxD_data(recfx_data));

	async_transmitter uart_transmitterfx(.clk(clk), .TxD_start(txdfx_start), .TxD_data(sendfx_data),
		.TxD(uart_tx), .TxD_busy(txdfx_busy));
		
	// instantiate packet demux
	packet_demux packet_demux(.clk(clk), .current_state(demux_state), .en(demux_en), .reset(reset_loader), .rx_ready(rxfx_done), .rx_data(recfx_data),
		.data_out(data), .current_count(demux_count), .addr_out(addr), .write_tick(write), .error_tick(checksum_error), .success_tick(success_tick));
 

	//state register
	always @(posedge clk, posedge reset)
	begin
		if(reset)
		begin
			state_reg <= idle;
			num_packets_reg <= 16'd0;
		end
		else
		begin
			state_reg <= state_next;
			num_packets_reg <= num_packets_next;
		end
	end


	// FSMD control path next-state logic
   always @*
   begin
	      state_next = state_reg; 
			num_packets_next = num_packets_reg;
			
			txdfx_start = 1'b0;
			sendfx_data = 8'h00;
			reset_loader = 1'b0;
			done_tick = 1'b0;
			
			case (state_reg)
				idle:
				begin
					if((recfx_data[7:0] == 8'b10000100) && rxfx_done)
					begin
							reset_loader = 1'b1; //reset loader and packet demux
							state_next = idle2;
					end
				end
				idle2:
				begin
					if(!rxfx_done)
						state_next = numpackets1;
				end
				numpackets1:
				begin
					if(rxfx_done)
					begin
							num_packets_next[7:0] = recfx_data;
							state_next = numpackets2;
					end
				end
				numpackets2:
				begin
					if(!rxfx_done)
						state_next = numpackets3;
				end
				numpackets3:
				begin
					if(rxfx_done)
					begin
							num_packets_next[15:8] = recfx_data;
							
							state_next = load;
					end
				end
				load:
				begin
					if(!rxfx_done)
						state_next = load2;
				end
				load2:
				begin
					
					if(success_tick)
					begin
						num_packets_next = num_packets_reg - 1;
						state_next = load3;
					end
					if(num_packets_reg[15:0] == 16'd0)
						state_next = done;
				end
				load3:
				begin
					if(!success_tick)
						state_next = load2;
				end
				done:
				begin
					done_tick = 1'b1;
					state_next = idle;
				end
				
				default: state_next = idle;
			endcase
	end
	
	
//output
	assign demux_en = (state_reg == load2);
	
//  wire [7:0] indata;
//  wire       insend;
//  //Rs232Rx uart(clk, UART_RX, indata, insend);
//  	async_receiver uart_receiver(.clk(clk), .RxD(UART_RX), .RxD_data_ready(insend), .RxD_data(indata));
//	
//  reg [1:0] state = 0;
//  reg [7:0] cksum;
//  reg [7:0] count;
//  wire [7:0] new_cksum = cksum + indata;
//  always @(posedge clk) if (RESET) begin
//    write <= 0;
//    state <= 0;
//    count <= 0;
//    cksum <= 0;
//    addr <= 0;
//    data <= 0;
//    checksum_error <= 0;
//  end else begin
//    write <= 0;
//    if (insend) begin
//      cksum <= new_cksum;
//      count <= count - 8'd1;
//      if (state == 0) begin
//        state <= 1;
//        cksum <= indata;
//      end else if (state == 1) begin
//        addr <= indata;
//        state <= 2;
//      end else if (state == 2) begin
//        count <= indata;
//        state <= 3;
//      end else begin
//        data <= indata;
//        write <= 1;
//        if (count == 1) begin
//          state <= 0;
//          if (new_cksum != 0)
//            checksum_error <= 1;
//        end
//      end
//    end
//  end
endmodule

