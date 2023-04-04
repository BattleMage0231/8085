class VMError(Exception):
    pass

class Registers:
    def __init__(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.PC = 0

# AC not supported
class Flags:
    def __init__(self):
        self.Cy = 0
        self.S = 0
        self.Z = 0
        self.P = 0

# big endian
class VM:
    RAM_SIZE = 64000 # bytes

    def __init__(self):
        self.regs = Registers()
        self.flags = Flags()
        self.mem = [0] * VM.RAM_SIZE
        self.halted = False
    
    def addr_chk(self, addr, error='Invalid address'):
        if addr < 0 or addr >= VM.RAM_SIZE:
            raise VMError(f'{error} {addr:04x}')
        return addr
    
    def get_single_arg(self):
        arg1 = self.mem[self.addr_chk(self.regs.PC + 1, 'Invalid arg1 address')]
        return arg1
    
    def get_double_arg(self):
        arg1 = self.mem[self.addr_chk(self.regs.PC + 1, 'Invalid arg1 address')]
        arg2 = self.mem[self.addr_chk(self.regs.PC + 2, 'Invalid arg2 address')]
        return (arg1, arg2)
    
    def set_flags(self, result):
        self.flags.Cy = 1 if result > 255 else 0
        result %= 255
        self.flags.S = 1 if result & 0b10000000 else 0
        self.flags.Z = 1 if result == 0 else 0
        self.flags.P = 1 if result % 2 == 0 else 0
        return result

    def execute_next(self):
        if self.halted:
            raise VMError('Cannot run a halted program')
        opcode = self.mem[self.addr_chk(self.regs.PC, 'Invalid PC address')]
        if opcode == 0x00: # NOP
            self.regs.PC += 1
        elif opcode == 0x06: # MVI B, arg1
            arg1 = self.get_single_arg()
            self.regs.B = arg1
            self.regs.PC += 2
        elif opcode == 0x0e: # MVI C, arg1
            arg1 = self.get_single_arg()
            self.regs.C = arg1
            self.regs.PC += 2
        elif opcode == 0x32: # STA arg1arg2
            arg1, arg2 = self.get_double_arg()
            addr = (arg1 << 8) | arg2
            self.mem[self.addr_chk(addr)] = self.regs.A
            self.regs.PC += 3
        elif opcode == 0x3a: # LDA arg1arg2
            arg1, arg2 = self.get_double_arg()
            addr = (arg1 << 8) | arg2
            self.regs.A = self.mem[self.addr_chk(addr)]
            self.regs.PC += 3
        elif opcode == 0x3e: # MVI A, arg1
            arg1 = self.get_single_arg()
            self.regs.A = arg1
            self.regs.PC += 2
        elif opcode == 0x76: # HLT
            self.halted = True
            self.regs.PC += 1
        elif opcode == 0xc6: # ADI arg1
            arg1 = self.get_single_arg()
            self.regs.A = self.set_flags(self.regs.A + arg1)
            self.regs.PC += 2
        else:
            raise VMError(f'Unknown instruction {opcode:02x}')
