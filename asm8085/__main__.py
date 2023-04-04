from assembler import Assembler
from vm import VM

program = """
MVI A,0F 
STA 1004
STA 1008
STA 100C
ADI 30
HLT
"""

a = Assembler(program)

while not a.done():
    a.assemble_next_line()

output = a.output
print(list([hex(x) for x in output]))

vm = VM()
for i in range(len(output)):
    vm.mem[i] = int(output[i])

print(vm.mem[:50])

while not vm.halted:
    vm.execute_next()
    print(vm.regs.PC, vm.regs.A)
