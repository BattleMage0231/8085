class VMError(Exception):
    pass

# AC not supported
class Flags:
    def __init__(self):
        self._Z = 0
        self._S = 0
        self._P = 0
        self._CY = 0
    
    @property
    def Z(self):
        return self._Z
    
    @Z.setter
    def Z(self, value):
        assert value == 0 or value == 1
        self._Z = value
    
    @property
    def S(self):
        return self._S
    
    @S.setter
    def S(self, value):
        assert value == 0 or value == 1
        self._S = value
    
    @property
    def P(self):
        return self._P
    
    @P.setter
    def P(self, value):
        assert value == 0 or value == 1
        self._P = value
    
    @property
    def CY(self):
        return self._CY
    
    @CY.setter
    def CY(self, value):
        assert value == 0 or value == 1
        self._CY = value

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
