from util import *
from registers import Registers

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

    def extract_enc(self, enc):
        return self.regs[enc] if enc != 0b110 else self.mem[self.regs.HL]

    def extract_src(self, opcode):
        return self.extract_enc(get_src(opcode))
    
    def extract_dest(self, opcode):
        return self.extract_enc(get_dest(opcode))

    def extract_rp(self, opcode):
        return self.extract_enc(get_rp(opcode))
    
    def apply_mov(self, val, dest):
        assert 0 <= val <= 0xff
        if dest == 0b110:
            self.mem[self.regs.HL] = val
        else:
            self.regs[dest] = val

    def apply_add(self, val):
        assert 0 <= val <= 0xff
        res = self.regs.A + val
        self.flags.CY = 1 if res > 255 else 0
        self.regs.A = res % 256
        self.flags.update_zsp(self.regs.A)
    
    def apply_add_carry(self, val):
        assert 0 <= val <= 0xff
        if val == 0xff and self.flags.CY == 1:
            self.flags.update_zsp(self.regs.A)
        else:
            self.apply_add(val + self.flags.CY)

    def apply_sub(self, val):
        assert 0 <= val <= 0xff
        res = self.regs.A - val
        self.flags.CY = 1 if res < 0 else 0
        self.regs.A = res % 256
        self.flags.update_zsp(self.regs.A)
    
    def apply_sub_borrow(self, val):
        assert 0 <= val <= 0xff
        if val == 0xff and self.flags.CY == 1:
            self.flags.update_zsp(self.regs.A)
        else:
            self.apply_sub(val + self.flags.CY)
        
    def apply_and(self, val):
        assert 0 <= val <= 0xff
        self.regs.A &= val
        self.flags.CY = 0
        self.flags.update_zsp(self.regs.A)
    
    def apply_or(self, val):
        assert 0 <= val <= 0xff
        self.regs.A |= val
        self.flags.CY = 0
        self.flags.update_zsp(self.regs.A)

    def apply_xor(self, val):
        assert 0 <= val <= 0xff
        self.regs.A ^= val
        self.flags.CY = 0
        self.flags.update_zsp(self.regs.A)

    def apply_cmp(self, val):
        assert 0 <= val <= 0xff
        res = self.regs.A - val
        self.flags.CY = 1 if res < 0 else 0
        self.flags.update_zsp(res % 256)

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
            val = self.extract_src(opcode)
            dest = get_dest(opcode)
            self.apply_mov(val, dest)
            self.regs.PC += 1
        elif opcode & 0xc7 == 0x06: # MVI
            dest = get_dest(opcode)
            arg = self.get_single_arg()
            self.apply_mov(arg, dest)
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
            addr = self.extract_rp(opcode)
            self.regs.A = self.mem[addr]
            self.regs.PC += 1
        elif opcode & 0xef == 0x02: # STAX
            addr = self.extract_rp(opcode)
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
            val = self.extract_src(opcode)
            self.apply_add(val)
            self.regs.PC += 1
        elif opcode == 0xc6: # ADI
            arg = self.get_single_arg()
            self.apply_add(arg)
            self.regs.PC += 2
        elif opcode & 0xf8 == 0x88: # ADC
            val = self.extract_src(opcode)
            self.apply_add_carry(val)
            self.regs.PC += 1
        elif opcode == 0xce: # ACI
            arg = self.get_single_arg()
            self.apply_add_carry(arg)
            self.regs.PC += 2
        elif opcode & 0xf8 == 0x90: # SUB
            val = self.extract_src(opcode)
            self.apply_sub(val)
            self.regs.PC += 1
        elif opcode == 0xd6: # SUI
            arg = self.get_single_arg()
            self.apply_sub(arg)
            self.regs.PC += 2
        elif opcode & 0xf8 == 0x98: # SBB
            val = self.extract_src(opcode)
            self.apply_sub_borrow(val)
            self.regs.PC += 1
        elif opcode == 0xde: # SBI
            arg = self.get_single_arg()
            self.apply_sub_borrow(arg)
            self.regs.PC += 2
        elif opcode & 0xc7 == 0x04: # INR
            dest = get_dest(opcode)
            val = self.extract_dest(opcode)
            res = (val + 0x01) & 0xff
            self.flags.update_zsp(res)
            if dest == 0b110:
                self.mem[self.regs.HL] = res
            else:
                self.regs[dest] = res
            self.regs.PC += 1
        elif opcode & 0xc7 == 0x05: # DCR
            dest = get_dest(opcode)
            val = self.extract_dest(opcode)
            res = (val + 0xff) & 0xff
            self.flags.update_zsp(res)
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
            val = self.extract_rp(opcode)
            res = self.regs.HL + val
            self.flags.CY = 1 if res > 0xffff else 0
            self.regs.HL = res & 0xffff
            self.regs.PC += 1
        elif opcode & 0xf8 == 0xa0: # ANA
            val = self.extract_src(opcode)
            self.apply_and(val)
            self.regs.PC += 1
        elif opcode == 0xe6: # ANI
            arg = self.get_single_arg()
            self.apply_and(arg)
            self.regs.PC += 2
        elif opcode & 0xf8 == 0xb0: # ORA
            val = self.extract_src(opcode)
            self.apply_or(val)
            self.regs.PC += 1
        elif opcode == 0xf6: # ORI
            arg = self.get_single_arg()
            self.apply_or(arg)
            self.regs.PC += 2
        elif opcode & 0xf8 == 0xa8: # XRA
            val = self.extract_src(opcode)
            self.apply_xor(val)
            self.regs.PC += 1
        elif opcode == 0xee: # XRI
            arg = self.get_single_arg()
            self.apply_xor(arg)
            self.regs.PC += 2
        elif opcode & 0xf8 == 0xb8: # CMP
            val = self.extract_src(opcode)
            self.apply_cmp(val)
            self.regs.PC += 1
        elif opcode == 0xfe: # CPI
            arg = self.get_single_arg()
            self.apply_cmp(arg)
            self.regs.PC += 2
        elif opcode == 0x07: # RLC
            self.flags.CY = self.regs.A >> 7
            self.regs.A = ((self.regs.A << 1) & 0xff) | (self.regs.A >> 7)
            self.regs.PC += 1
        elif opcode == 0x0f: # RRC
            self.flags.CY = self.regs.A & 1
            self.regs.A = ((self.regs.A & 1) << 7) | (self.regs.A >> 1)
            self.regs.PC += 1
        elif opcode == 0x17: # RAL
            msb = self.regs.A >> 7
            self.regs.A = ((self.regs.A << 1) & 0xff) | self.flags.CY
            self.flags.CY = msb
            self.regs.PC += 1
        elif opcode == 0x1f: # RAR
            lsb = self.regs.A & 1
            self.regs.A = (self.flags.CY << 7) | (self.regs.A >> 1)
            self.flags.CY = lsb
            self.regs.PC += 1
        elif opcode == 0x2f: # CMA
            self.regs.A ^= 0xff
            self.regs.PC += 1
        elif opcode == 0x3f: # CMC
            self.flags.CY ^= 1
            self.regs.PC += 1
        elif opcode == 0x37: # STC
            self.flags.CY = 1
            self.regs.PC += 1
        else:
            raise VMError(f'Unknown instruction {opcode:02x}')
