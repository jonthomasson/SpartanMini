
# PlanAhead Launch Script for Post-Synthesis floorplanning, created by Project Navigator

create_project -name NES_Nexys4 -dir "C:/Users/Stache/Documents/Xilinx_Projects/NES/nexys3_ver4/handyvgs/xilinx/planAhead_run_3" -part xc6slx16csg324-3
set_property design_mode GateLvl [get_property srcset [current_run -impl]]
set_property edif_top_file "C:/Users/Stache/Documents/Xilinx_Projects/NES/nexys3_ver4/handyvgs/xilinx/NES_Nexys4.ngc" [ get_property srcset [ current_run ] ]
add_files -norecurse { {C:/Users/Stache/Documents/Xilinx_Projects/NES/nexys3_ver4/handyvgs/xilinx} }
set_property target_constrs_file "C:/Users/Stache/Documents/Xilinx_Projects/NES/nexys3_ver4/handyvgs/src/Nexys4_Master.ucf" [current_fileset -constrset]
add_files [list {C:/Users/Stache/Documents/Xilinx_Projects/NES/nexys3_ver4/handyvgs/src/Nexys4_Master.ucf}] -fileset [get_property constrset [current_run]]
link_design
