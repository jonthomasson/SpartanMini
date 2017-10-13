'''
LEON3 trap types from manual
'''

named_traps = '''
reset
0x00
write error
0x2b
instruction_access_error
0x01
illegal_instruction
0x02
privileged_instruction
0x03
fp_disabled
0x04
cp_disabled
0x24
watchpoint_detected
0x0B
window_overflow
0x05
window_underflow
0x06
register_hadrware_error
0x20
mem_address_not_aligned
0x07
fp_exception
0x08
cp_exception
0x28
data_access_exception
0x09
tag_overflow
0x0A
divide_exception
0x2A
interrupt_level_1
0x11
interrupt_level_2
0x12
interrupt_level_3
0x13
interrupt_level_4
0x14
interrupt_level_5
0x15
interrupt_level_6
0x16
interrupt_level_7
0x17
interrupt_level_8
0x18
interrupt_level_9
0x19
interrupt_level_10
0x1A
interrupt_level_11
0x1B
interrupt_level_12
0x1C
interrupt_level_13
0x1D
interrupt_level_14
0x1E
interrupt_level_15
0x1F
'''

traptypes = ['unknown trap 0x%02x' % i for i in range(128)]
traptypes += ['software trap ta 0x%02x' % i for i in range(128)]

named_traps = [x for x in named_traps.splitlines() if x.strip()]
named_traps = zip(named_traps[0::2], named_traps[1::2])
named_traps = [(x, int(y, 0)) for (x, y) in named_traps]

for name, value in named_traps:
    traptypes[value] = name
