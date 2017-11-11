`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Jon Thomasson
// 
// Create Date:    15:23:38 11/25/2016 
// Design Name: 
// Module Name:    packet_demux 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
// Decodes incoming UART signals and demuxes them into addr/data lines.
// This is a simple state machine which translates the checksum, count, address, and data for each packet sent from the pc.
// Packet Format: 
//   1 byte checksum | 1 byte address | 1 byte count | (count + 1) data bytes
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module packet_demux(
input clk, input reset, input en,
input rx_ready, input [7:0] rx_data, 
output reg [7:0] data_out, 
output reg [7:0] addr_out, output reg write_tick, 
output reg error_tick, output reg success_tick,
output wire [7:0] current_state, current_count
    );

   // symbolic state declaration
   localparam  [3:0]
               idle  = 4'b0000,
					idle2 = 4'b0001,
               checksum = 4'b0010,
					checksum2 = 4'b0011,
               address   = 4'b0100,
					address2 = 4'b0101,
               count = 4'b0110,
					count2 = 4'b0111,
					data = 4'b1000,
					data2 = 4'b1001,
					validate = 4'b1010;


   // signal declaration
   reg [3:0] state_reg, state_next;
	
	reg [7:0] checksum_reg, checksum_next, count_reg, count_next, address_reg;

   // body
   // fsmd state & data registers
    always @(posedge clk, posedge reset)
       if (reset)
          begin
             state_reg <= idle;
				 count_reg <= 8'd0;
				 checksum_reg <= 8'd0;
          end
       else
          begin
             state_reg <= state_next;
				 count_reg <= count_next;
				 checksum_reg <= checksum_next;
          end
			 

   // FSMD control path next-state logic
   always @*
   begin
		state_next = state_reg; 
		count_next = count_reg;
		checksum_next = checksum_reg;
		write_tick = 1'b0;			 
		success_tick = 1'b0;
		error_tick = 1'b0;

      case (state_reg)
         idle:
            begin
               if (rx_ready && en) //only starting idle once enable is held high
                  begin
                     state_next = idle2;
                     checksum_next = rx_data;
							$display ("state = idle"); 
                  end
            end
			idle2:
				begin
					if(!rx_ready)
						state_next = checksum;
				end
         checksum:
            begin
               if (rx_ready)
                  begin
                     state_next = checksum2;
							addr_out = rx_data;
                     checksum_next = checksum_reg + rx_data;
							$display ("state = checksum");
                  end
            end
			checksum2:
				begin
					if(!rx_ready)
						state_next = address;
				end
         address:
            begin
               if (rx_ready)
                  begin
                     state_next = address2;
							count_next = rx_data;
                     checksum_next = checksum_reg + rx_data;
							$display ("state = address");
                  end
            end
			address2:
				begin
					if(!rx_ready)
						state_next = count;
				end
         count:
            begin
               if (rx_ready)
                  begin
                     state_next = count2;
							data_out = rx_data;
							write_tick = 1'b1;
                     checksum_next = checksum_reg + rx_data;
							$display ("state = count");
                  end
            end
			count2:
				begin
					if(!rx_ready)
						state_next = data;
				end
			data:
            begin
					
					if (count_reg == 1)
						begin
							state_next = validate;
						end
					else
               if (rx_ready)
                  begin
							$display ("state = data");
                     state_next = data2;
							data_out = rx_data;
							write_tick = 1'b1;
							count_next = count_reg - 1;
                     checksum_next = checksum_reg + rx_data;
							
                  end
            end
			data2:
				begin
					if(!rx_ready)
						state_next = data;
				end
			validate:
				begin
					$display ("state = validate");
					$display("checksum = %b", checksum_reg);
					if (checksum_reg == 0)
					begin
						success_tick = 1'b1;
					end
					else
					begin
						error_tick = 1'b1;
					end
					
					if(!rx_ready)
						state_next = idle;
					
				end
         default: state_next = idle;
      endcase
   end
	
	assign current_state = state_reg;
	assign current_count = count_reg;
endmodule
