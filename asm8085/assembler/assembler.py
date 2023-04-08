import string

class SyntaxError(Exception):
    pass

class Assembler:
    def __init__(self, program):
        self.program = program
        self.index = 0
        self.output = b''
        self.line = 1

    def done(self):
        return self.index == len(self.program)

    def cur(self):
        return self.program[self.index]
    
    def err(self, msg='Error'):
        raise SyntaxError(f'{msg} on line {self.line}')
    
    def emit(self, byte):
        self.output += byte.to_bytes(1, byteorder='big')

    def skip_whitespace(self):
        while self.index < len(self.program):
            cur = self.program[self.index]
            if cur not in '; \t\r':
                return
            if cur == ';':
                self.index += 1
                while not self.done() and self.cur() != '\n':
                    self.index += 1
                return
            self.index += 1
    
    def space_chk(self, msg='Error'):
        self.skip_whitespace()
        if self.done() or self.cur() == '\n':
            self.err(msg)

    def char_skip(self, chr, msg=f'Expected {chr}'):
        if self.cur() != chr:
            self.err(msg)
        self.index += 1

    def parse_string(self, msg='Expected string'):
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        if self.done() or self.cur() not in alphabet:
            self.err(msg)
        ident = ''
        while not self.done() and self.cur() in alphabet:
            ident += self.cur()
            self.index += 1
        return ident
    
    def as_hex_byte(self, string):
        try:
            val = int(string, 16)
            if val < 0 or val > 255:
                self.err(f'"{val}" does not fit in a byte')
            return val
        except ValueError:
            self.err(f'Cannot interpret "{string}" as byte')
    
    def as_hex_two_bytes(self, string):
        try:
            val = int(string, 16)
            if val < 0 or val > 65535:
                self.err(f'"{val}" does not fit in 2 bytes')
            return val
        except ValueError:
            self.err(f'Cannot interpret "{string}" as 2 bytes')
    
    def assemble_next_line(self):
        if self.done():
            self.err('No more to assemble')
        self.skip_whitespace()
        # check for empty line
        if self.done():
            return
        if self.cur() == '\n':
            self.line += 1
            self.index += 1
            return    
        # get instruction mnemonic
        op = self.parse_string('Expected instruction')
        if op == 'NOP':
            self.emit(0x00)
        elif op == 'MVI':
            self.space_chk('Expected argument 1 to MVI')
            arg1 = self.parse_string('Expected argument 1 to MVI')
            self.char_skip(',')
            # argument 1
            if arg1 == 'A':
                self.emit(0x3e)
            elif arg1 == 'B':
                self.emit(0x06)
            elif arg1 == 'C':
                self.emit(0x0e)
            else:
                self.err(f'Unknown argument 1 to MVI "{arg1}"')
            # argument 2
            self.space_chk('Expected argument 2 to MVI')
            arg2 = self.parse_string('Expected argument 2 to MVI')
            arg2 = self.as_hex_byte(arg2)
            self.emit(arg2)
        elif op == 'STA':
            self.emit(0x32)
            self.space_chk('Expected argument to STA')
            arg = self.parse_string('Expected argument to STA')
            arg = self.as_hex_two_bytes(arg)
            top = arg >> 8
            bottom = arg & 0xff
            self.emit(bottom)
            self.emit(top)
        elif op == 'LDA':
            self.emit(0x3a)
            self.space_chk('Expected argument to STA')
            arg = self.parse_string('Expected argument to STA')
            arg = self.as_hex_two_bytes(arg)
            top = arg >> 8
            bottom = arg & 0xff
            self.emit(bottom)
            self.emit(top)
        elif op == 'HLT':
            self.emit(0x76)
        elif op == 'ADI':
            self.emit(0xc6)
            self.space_chk('Expected argument to ADI')
            arg = self.parse_string('Expected argument to ADI')
            arg = self.as_hex_byte(arg)
            self.emit(arg)
        else:
            self.err(f'Unknown instruction "{op}"')
        self.skip_whitespace()
        if self.cur() == '\n':
            self.line += 1
            self.index += 1
        elif not self.done():
            self.err('Expected new line')
