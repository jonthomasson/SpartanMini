
# PlanAhead Launch Script for Pre-Synthesis Floorplanning, created by Project Navigator

create_project -name NES_Nexys4 -dir "C:/Users/Stache/Documents/Xilinx Projects/fpganes3/xilinx/planAhead_run_1" -part xc7a100tcsg324-1
set_param project.pinAheadLayout yes
set srcset [get_property srcset [current_run -impl]]
set_property target_constrs_file "C:/Users/Stache/Documents/Xilinx Projects/fpganes3/src/Nexys4_Master.ucf" [current_fileset -constrset]
set hdlfile [add_files [list {../src/compat.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/vga.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/nes.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/hw_uart.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/hw_sound.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/hw_led.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/hq2x.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/clk_wiz_v3_6.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../src/NES_Nexys4.v}]]
set_property file_type Verilog $hdlfile
set_property library work $hdlfile
set_property top NES_Nexys4 $srcset
add_files [list {C:/Users/Stache/Documents/Xilinx Projects/fpganes3/src/Nexys4_Master.ucf}] -fileset [get_property constrset [current_run]]
open_rtl_design -part xc7a100tcsg324-1
