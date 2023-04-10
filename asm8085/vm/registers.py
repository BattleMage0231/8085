class Registers:
    def __init__(self):
        self._A = 0
        self._B = 0
        self._C = 0
        self._D = 0
        self._E = 0
        self._H = 0
        self._L = 0
        self._PC = 0
        self._SP = 0
    
    @property
    def A(self):
        return self._A
    
    @A.setter
    def A(self, value):
        assert 0 <= value <= 0xff
        self._A = value
    
    @property
    def B(self):
        return self._B
    
    @B.setter
    def B(self, value):
        assert 0 <= value <= 0xff
        self._B = value

    @property
    def C(self):
        return self._C
    
    @C.setter
    def C(self, value):
        assert 0 <= value <= 0xff
        self._C = value

    @property
    def D(self):
        return self._D
    
    @D.setter
    def D(self, value):
        assert 0 <= value <= 0xff
        self._D = value

    @property
    def E(self):
        return self._E
    
    @E.setter
    def E(self, value):
        assert 0 <= value <= 0xff
        self._E = value

    @property
    def H(self):
        return self._H
    
    @H.setter
    def H(self, value):
        assert 0 <= value <= 0xff
        self._H = value

    @property
    def L(self):
        return self._L
    
    @L.setter
    def L(self, value):
        assert 0 <= value <= 0xff
        self._L = value

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

    @property
    def PC(self):
        return self._PC
    
    @PC.setter
    def PC(self, value):
        assert 0 <= value <= 0xffff
        self._PC = value

    @property
    def SP(self):
        return self._SP
    
    @SP.setter
    def SP(self, value):
        assert 0 <= value <= 0xffff
        self._SP = value
    
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
