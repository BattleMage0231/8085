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
        assert 0 <= value <= 0xffff
        self.B = value >> 8
        self.C = value & 0xff
    
    @property
    def DE(self):
        return (self.D << 8) | self.E
    
    @DE.setter
    def DE(self, value):
        assert 0 <= value <= 0xffff
        self.D = value >> 8
        self.E = value & 0xff
    
    @property
    def HL(self):
        return (self.H << 8) | self.L
    
    @HL.setter
    def HL(self, value):
        assert 0 <= value <= 0xffff
        self.H = value >> 8
        self.L = value & 0xff
    
    def __getitem__(self, enc):
        if enc == 0b0000:
            return self.B
        elif enc == 0b0001:
            return self.C
        elif enc == 0b0010:
            return self.D
        elif enc == 0b0011:
            return self.E
        elif enc == 0b0100:
            return self.H
        elif enc == 0b0101:
            return self.L
        elif enc == 0b0111:
            return self.A
        elif enc == 0b1000:
            return self.BC
        elif enc == 0b1001:
            return self.DE
        elif enc == 0b1010:
            return self.HL
        elif enc == 0b1011:
            return self.SP
        else:
            raise IndexError(f'Unknown register encoding {enc:04b}')

    def __setitem__(self, enc, val):
        assert 0 <= val <= (0xff if enc & 0b1000 == 0 else 0xffff)
        if enc == 0b0000:
            self.B = val
        elif enc == 0b0001:
            self.C = val
        elif enc == 0b0010:
            self.D = val
        elif enc == 0b0011:
            self.E = val
        elif enc == 0b0100:
            self.H = val
        elif enc == 0b0101:
            self.L = val
        elif enc == 0b0111:
            self.A = val
        elif enc == 0b1000:
            self.BC = val
        elif enc == 0b1001:
            self.DE = val
        elif enc == 0b1010:
            self.HL = val
        elif enc == 0b1011:
            self.SP = val
        else:
            raise IndexError(f'Unknown register encoding {enc:04b}')

# AC not supported
class Flags:
    def __init__(self):
        self.Z = 0
        self.S = 0
        self.P = 0
        self.CY = 0

    def update_zsp(self, val):
        assert 0 <= val <= 0xff
        self.Z = 1 if val & 0xff == 0 else 0
        self.S = 1 if val & 0x80 != 0 else 0
        self.P = 1 if bin(val & 0xff).count('1') % 2 == 0 else 0

    def as_byte(self):
        return (self.S << 7) | (self.Z << 6) | (self.P << 2) | self.CY

class Memory:
    def __init__(self, size):
        self.len = size
        self.content = [0] * size
    
    def __len__(self):
        return self.len
    
    def __getitem__(self, idx):
        assert idx >= 0
        if idx >= self.len:
            raise VMError('Invalid address')
        return self.content[idx]
    
    def __setitem__(self, idx, val):
        assert idx >= 0
        assert 0 <= val <= 0xff
        if idx >= self.len:
            raise VMError('Invalid address')
        self.content[idx] = val

def get_src(opcode):
    assert 0 <= opcode <= 0xff
    return opcode & 0x07

def get_dest(opcode):
    assert 0 <= opcode <= 0xff
    return (opcode & 0x38) >> 3
        
def get_rp(opcode):
    assert 0 <= opcode <= 0xff
    return ((opcode & 0x30) >> 4) | 0b1000
