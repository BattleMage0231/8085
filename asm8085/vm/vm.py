from util import *

class VM:
    RAM_SIZE = 64000 # bytes

    def __init__(self):
        self.regs = Registers()
        self.flags = Flags()
        self.mem = Memory(VM.RAM_SIZE)
        self.halted = False
    
    def get_single_arg(self):
        return self.mem[self.regs.PC + 1]
    
    def get_double_arg(self):
        arg1 = self.mem[self.regs.PC + 1]
        arg2 = self.mem[self.regs.PC + 2]
        return (arg2 << 8) | arg1

    def execute_next(self):
        if self.halted:
            raise VMError('Cannot run a halted program')
        opcode = self.mem[self.regs.PC]
        if opcode == 0x00: # NOP
            self.regs.PC += 1
        elif opcode == 0x76: # HLT
            self.halted = True
            self.regs.PC += 1
        elif opcode != 0x76 and opcode & 0xc0 == 0x40: # MOV
            src = get_src(opcode)
            dest = get_dest(opcode)
            if src == 0b110:
                self.regs[dest] = self.mem[self.regs.HL]
            elif dest == 0b110:
                self.mem[self.regs.HL] = self.regs[src]
            else:
                self.regs[dest] = self.regs[src]
            self.regs.PC += 1
        elif opcode & 0xc7 == 0x06: # MVI
            dest = get_dest(opcode)
            arg = self.get_single_arg()
            if dest == 0b110:
                self.mem[self.regs.HL] = arg
            else:
                self.regs[dest] = arg
            self.regs.PC += 2
        elif opcode == 0x3a: # LDA
            addr = self.get_double_arg()
            self.regs.A = self.mem[addr]
            self.regs.PC += 3
        elif opcode == 0x32: # STA
            addr = self.get_double_arg()
            self.mem[addr] = self.regs.A
            self.regs.PC += 3
        elif opcode == 0x2a: # LHLD
            addr = self.get_double_arg()
            self.regs.L = self.mem[addr]
            self.regs.H = self.mem[addr + 1]
            self.regs.PC += 3
        elif opcode == 0x22: # SHLD
            addr = self.get_double_arg()
            self.mem[addr] = self.regs.L
            self.mem[addr + 1] = self.regs.H
            self.regs.PC += 3
        elif opcode & 0xcf == 0x01: # LXI
            rp = get_rp(opcode)
            arg = self.get_double_arg()
            self.regs[rp] = arg
            self.regs.PC += 3
        elif opcode & 0xef == 0x0a: # LDAX
            rp = get_rp(opcode)
            self.regs.A = self.mem[self.regs[rp]]
            self.regs.PC += 1
        elif opcode & 0xef == 0x02: # STAX
            rp = get_rp(opcode)
            addr = self.regs[rp]
            self.mem[addr] = self.regs.A
            self.regs.PC += 1
        elif opcode == 0xeb: # XCHG
            self.regs.HL, self.regs.DE = self.regs.DE, self.regs.HL
            self.regs.PC += 1
        elif opcode == 0xe3: # XTHL
            idx1 = self.regs.SP
            idx2 = self.regs.SP + 1
            self.mem[idx1], self.regs.L = self.regs.L, self.mem[idx1]
            self.mem[idx2], self.regs.H = self.regs.H, self.mem[idx2]
            self.regs.PC += 1
        elif opcode & 0xf8 == 0x80: # ADD
            src = get_src(opcode)
            val = self.regs[src] if src != 0b110 else self.mem[self.regs.HL]
            res = self.regs.A + val
            self.flags.update(res)
            self.regs.A = res & 0xff
            self.regs.PC += 1
        elif opcode == 0xc6: # ADI
            arg = self.get_single_arg()
            res = self.regs.A + arg
            self.flags.update(res)
            self.regs.A = res & 0xff
            self.regs.PC += 2
        elif opcode & 0xf8 == 0x88: # ADC
            src = get_src(opcode)
            val = self.regs[src] if src != 0b110 else self.mem[self.regs.HL]
            res = self.regs.A + val + self.flags.CY
            self.flags.update(res)
            self.regs.A = res & 0xff
            self.regs.PC += 1
        elif opcode == 0xce: # ACI
            arg = self.get_single_arg()
            res = self.regs.A + arg + self.flags.CY
            self.flags.update(res)
            self.regs.A = res & 0xff
            self.regs.PC += 2
        elif opcode & 0xf8 == 0x90: # SUB
            src = get_src(opcode)
            val = self.regs[src] if src != 0b110 else self.mem[self.regs.HL]
            res = self.regs.A + compl(val)
            self.flags.update(res)
            self.flags.CY ^= 1
            self.regs.A = res & 0xff
            self.regs.PC += 1
        elif opcode == 0xd6: # SUI
            arg = compl(self.get_single_arg())
            res = self.regs.A + arg
            self.flags.update(res)
            self.flags.CY ^= 1
            self.regs.A = res & 0xff
            self.regs.PC += 2
        elif opcode & 0xf8 == 0x98: # SBB
            src = get_src(opcode)
            val = self.regs[src] if src != 0b110 else self.mem[self.regs.HL]
            res = self.regs.A + compl((val + self.flags.CY) & 0xff)
            self.flags.update(res)
            self.flags.CY ^= 1
            self.regs.A = res & 0xff
            self.regs.PC += 1
        elif opcode == 0xde: # SBI
            arg = self.get_single_arg()
            res = self.regs.A + compl((arg + self.flags.CY) & 0xff)
            self.flags.update(res)
            self.flags.CY ^= 1
            self.regs.A = res & 0xff
            self.regs.PC += 2
        elif opcode & 0xc7 == 0x04: # INR
            dest = get_dest(opcode)
            val = self.regs[dest] if dest != 0b110 else self.mem[self.regs.HL]
            res = (val + 0x01) & 0xff
            CY = self.flags.CY
            self.flags.update(res)
            self.flags.CY = CY
            if dest == 0b110:
                self.mem[self.regs.HL] = res
            else:
                self.regs[dest] = res
            self.regs.PC += 1
        elif opcode & 0xc7 == 0x05: # DCR
            dest = get_dest(opcode)
            val = self.regs[dest] if dest != 0b110 else self.mem[self.regs.HL]
            res = (val + 0xff) & 0xff
            CY = self.flags.CY
            self.flags.update(res)
            self.flags.CY = CY
            if dest == 0b110:
                self.mem[self.regs.HL] = res
            else:
                self.regs[dest] = res
            self.regs.PC += 1
        elif opcode & 0xcf == 0x03: # INX
            rp = get_rp(opcode)
            res = (self.regs[rp] + 0x0001) & 0xffff
            self.regs[rp] = res
            self.regs.PC += 1
        elif opcode & 0xcf == 0x0b: # DCX
            rp = get_rp(opcode)
            res = (self.regs[rp] + 0xffff) & 0xffff
            self.regs[rp] = res
            self.regs.PC += 1
        elif opcode & 0xcf == 0x09: # DAD
            rp = get_rp(opcode)
            res = self.regs.HL + self.regs[rp]
            self.flags.CY = 1 if res > 0xffff else 0
            self.regs.HL = res & 0xffff
            self.regs.PC += 1
        else:
            raise VMError(f'Unknown instruction {opcode:02x}')
