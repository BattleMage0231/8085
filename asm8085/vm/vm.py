class VMError(Exception):
    pass

class Registers:
    def __init__(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.PC = 0
        self.SP = 0
    
    @property
    def BC(self):
        return (self.B << 8) | self.C
    
    @BC.setter
    def BC(self, value):
        self.B = value >> 8
        self.C = value & 0xff
    
    @property
    def DE(self):
        return (self.D << 8) | self.E
    
    @DE.setter
    def DE(self, value):
        self.D = value >> 8
        self.E = value & 0xff
    
    @property
    def HL(self):
        return (self.H << 8) | self.L
    
    @HL.setter
    def HL(self, value):
        self.H = value >> 8
        self.L = value & 0xff

# AC not supported
class Flags:
    def __init__(self):
        self.Z = 0
        self.S = 0
        self.P = 0
        self.CY = 0

def popcnt(val):
    return bin(val).count('1')

def compl(val):
    return ((val ^ 0xff) + 1) & 0xff

def match(opcode, form):
    rep = f'{opcode:08b}'
    for i in range(8):
        if form[i] not in 'SDRrPC*' and form[i] != rep[i]:
            return False
    return True

class VM:
    RAM_SIZE = 64000 # bytes

    def __init__(self):
        self.regs = Registers()
        self.flags = Flags()
        self.mem = [0] * VM.RAM_SIZE
        self.halted = False
    
    def addr_chk(self, addr, error):
        if addr >= VM.RAM_SIZE:
            raise VMError(f'{error} {addr:04x}')
        return addr
    
    def get_mem(self, addr, error='Invalid address'):
        return self.mem[self.addr_chk(addr, error)]
    
    def set_mem(self, addr, val, error='Invalid address'):
        self.mem[self.addr_chk(addr, error)] = val
    
    def get_single_arg(self):
        return self.get_mem(self.regs.PC + 1, 'Invalid argument address')
    
    def get_double_arg(self):
        arg1 = self.get_mem(self.regs.PC + 1, 'Invalid argument 1 address')
        arg2 = self.get_mem(self.regs.PC + 2, 'Invalid argument 2 address')
        return (arg2 << 8) | arg1

    def get_reg_or_mem(self, enc):
        if enc == 0b000:
            return self.regs.B
        elif enc == 0b001:
            return self.regs.C
        elif enc == 0b010:
            return self.regs.D
        elif enc == 0b011:
            return self.regs.E
        elif enc == 0b100:
            return self.regs.H
        elif enc == 0b101:
            return self.regs.L
        elif enc == 0b110:
            return self.get_mem(self.regs.HL, 'Invalid address in [HL]')
        elif enc == 0b111:
            return self.regs.A
    
    def set_reg_or_mem(self, val, enc):
        if enc == 0b000:
            self.regs.B = val
        elif enc == 0b001:
            self.regs.C = val
        elif enc == 0b010:
            self.regs.D = val
        elif enc == 0b011:
            self.regs.E = val
        elif enc == 0b100:
            self.regs.H = val
        elif enc == 0b101:
            self.regs.L = val
        elif enc == 0b110:
            self.set_mem(self.regs.HL, val)
        elif enc == 0b111:
            self.regs.A = val
    
    def get_src(self, opcode):
        return self.get_reg_or_mem(opcode & 0x07)
    
    def get_dest(self, opcode):
        return self.get_reg_or_mem((opcode & 0x38) >> 3)
    
    def set_dest(self, val, opcode):
        self.set_reg_or_mem(val, (opcode & 0x38) >> 3)
    
    def get_reg_pair(self, enc):
        if enc == 0b00:
            return self.regs.BC
        elif enc == 0b01:
            return self.regs.DE
        elif enc == 0b10:
            return self.regs.HL
        elif enc == 0b11:
            return self.regs.SP
    
    def set_reg_pair(self, val, enc):
        if enc == 0b00:
            self.regs.BC = val
        elif enc == 0b01:
            self.regs.DE = val
        elif enc == 0b10:
            self.regs.HL = val
        elif enc == 0b11:
            self.regs.SP = val
        
    def get_rp(self, opcode):
        return self.get_reg_pair((opcode & 0x30) >> 4)
    
    def set_rp(self, val, opcode):
        self.set_reg_pair(val, (opcode & 0x30) >> 4)

    def execute_next(self):
        if self.halted:
            raise VMError('Cannot run a halted program')
        opcode = self.get_mem(self.regs.PC, 'Invalid PC address')
        if opcode == 0x00: # NOP
            self.regs.PC += 1
        elif match(opcode, '01DDDSSS'): # MOV/HLT
            self.regs.PC += 1
            if opcode == 0x76:
                self.halted = True
            else:
                val = self.get_src(opcode)
                self.set_dest(val, opcode)
        elif match(opcode, '00DDD110'): # MVI
            arg = self.get_single_arg()
            self.regs.PC += 2
            self.set_dest(arg, opcode)
        elif opcode == 0x3a: # LDA
            addr = self.get_double_arg()
            self.regs.PC += 3
            self.regs.A = self.get_mem(addr)
        elif opcode == 0x32: # STA
            addr = self.get_double_arg()
            self.regs.PC += 3
            self.set_mem(addr, self.regs.A)
        elif opcode == 0x2a: # LHLD
            addr = self.get_double_arg()
            self.regs.PC += 3
            self.regs.L = self.get_mem(addr)
            self.regs.H = self.get_mem(addr + 1)
        elif opcode == 0x22: # SHLD
            addr = self.get_double_arg()
            self.regs.PC += 3
            self.set_mem(addr, self.regs.L)
            self.set_mem(addr + 1, self.regs.H)
        elif match(opcode, '00RP0001'): # LXI
            arg = self.get_double_arg()
            self.regs.PC += 3
            self.set_rp(arg, opcode)
        elif match(opcode, '000r1010'): # LDAX
            self.regs.PC += 1
            self.regs.A = self.get_mem(self.get_rp(opcode))
        elif match(opcode, '000r0010'): # STAX
            self.regs.PC += 1
            addr = self.get_rp(opcode)
            self.set_mem(addr, self.regs.A)
        elif opcode == 0xeb: # XCHG
            self.regs.PC += 1
            self.regs.HL, self.regs.DE = self.regs.DE, self.regs.HL
        elif opcode == 0xe3: # XTHL
            self.regs.PC += 1
            tmp = self.get_mem(self.regs.SP)
            self.set_mem(self.regs.SP, self.regs.L)
            self.regs.L = tmp
            tmp = self.get_mem(self.regs.SP + 1)
            self.set_mem(self.regs.SP + 1, self.regs.H)
            self.regs.H = tmp
        else:
            raise VMError(f'Unknown instruction {opcode:02x}')