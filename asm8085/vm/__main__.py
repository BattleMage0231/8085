import unittest
from vm import VMError, Registers, Flags, VM

class ControlTest(unittest.TestCase):
    def test_nop(self):
        vm = VM()
        vm.execute_next()
        self.assertEqual(vm.regs.PC, 1)
    
    def test_hlt(self):
        vm = VM()
        vm.mem[0] = 0x76
        vm.execute_next()
        self.assertTrue(vm.halted)
        self.assertEqual(vm.regs.PC, 1)

class DataTransferTest(unittest.TestCase):
    def test_mov_reg_to_reg(self):
        vm = VM()
        vm.mem[0] = 0x4c # MOV C, H
        vm.regs.H = 0x12
        vm.execute_next()
        self.assertEqual(vm.regs.C, 0x12)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_mov_reg_to_mem(self):
        vm = VM()
        vm.mem[0] = 0x77 # MOV M, A
        vm.regs.A = 0x33
        vm.regs.HL = 0x1234
        vm.execute_next()
        self.assertEqual(vm.mem[0x1234], 0x33)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_mov_mem_to_reg(self):
        vm = VM()
        vm.mem[0] = 0x46 # MOV B, M
        vm.regs.HL = 0x3333
        vm.mem[0x3333] = 0x11
        vm.execute_next()
        self.assertEqual(vm.regs.B, 0x11)
        self.assertEqual(vm.regs.PC, 1)

    def test_mvi_reg(self):
        vm = VM()
        # MVI D, F2
        vm.mem[0] = 0x16
        vm.mem[1] = 0xf2
        vm.execute_next()
        self.assertEqual(vm.regs.D, 0xf2)
        self.assertEqual(vm.regs.PC, 2)
    
    def test_mvi_mem(self):
        vm = VM()
        # MVI M, E3
        vm.mem[0] = 0x36
        vm.mem[1] = 0xe3
        vm.regs.HL = 0x3412
        vm.execute_next()
        self.assertEqual(vm.mem[0x3412], 0xe3)
        self.assertEqual(vm.regs.PC, 2)
    
    def test_lda(self):
        vm = VM()
        # LDA 4F19
        vm.mem[0] = 0x3a
        vm.mem[1] = 0x19
        vm.mem[2] = 0x4f
        vm.mem[0x4f19] = 0x5a
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x5a)
        self.assertEqual(vm.regs.PC, 3)
    
    def test_sta(self):
        vm = VM()
        # STA BA5F
        vm.mem[0] = 0x32
        vm.mem[1] = 0x5f
        vm.mem[2] = 0xba
        vm.regs.A = 0xb9
        vm.execute_next()
        self.assertEqual(vm.mem[0xba5f], 0xb9)
        self.assertEqual(vm.regs.PC, 3)
    
    def test_lhld(self):
        vm = VM()
        # LHLD 0101
        vm.mem[0] = 0x2a
        vm.mem[1] = 0x01
        vm.mem[2] = 0x01
        vm.mem[0x0101] = 0x45
        vm.mem[0x0102] = 0x7f
        vm.execute_next()
        self.assertEqual(vm.regs.HL, 0x7f45)
        self.assertEqual(vm.regs.PC, 3)
    
    def test_shld(self):
        vm = VM()
        # SHLD DEF2
        vm.mem[0] = 0x22
        vm.mem[1] = 0xf2
        vm.mem[2] = 0xde
        vm.regs.HL = 0x0123
        vm.execute_next()
        self.assertEqual(vm.mem[0xdef2], 0x23)
        self.assertEqual(vm.mem[0xdef3], 0x01)
        self.assertEqual(vm.regs.PC, 3)
    
    def test_lxi(self):
        vm = VM()
        # LXI BC, 09C9
        vm.mem[0] = 0x01
        vm.mem[1] = 0xc9
        vm.mem[2] = 0x09
        vm.execute_next()
        self.assertEqual(vm.regs.BC, 0x09c9)
        self.assertEqual(vm.regs.PC, 3)
    
    def test_ldax(self):
        vm = VM()
        vm.mem[0] = 0x1a # LDAX DE
        vm.regs.DE = 0x5f6e
        vm.mem[0x5f6e] = 0xd4
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0xd4)
        self.assertEqual(vm.regs.PC, 1)

    def test_stax(self):
        vm = VM()
        vm.mem[0] = 0x02 # STAX BC
        vm.regs.A = 0x10
        vm.regs.BC = 0x0800
        vm.execute_next()
        self.assertEqual(vm.mem[0x0800], 0x10)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_xchg(self):
        vm = VM()
        vm.mem[0] = 0xeb # XCHG
        vm.regs.HL = 0x1234
        vm.regs.DE = 0x5678
        vm.execute_next()
        self.assertEqual(vm.regs.HL, 0x5678)
        self.assertEqual(vm.regs.DE, 0x1234)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_xthl(self):
        vm = VM()
        vm.mem[0] = 0xe3 # XTHL
        vm.regs.SP = 0x40f1
        vm.mem[0x40f1] = 0x40
        vm.regs.HL = 0x1234
        vm.execute_next()
        self.assertEqual(vm.regs.HL, 0x0040)
        self.assertEqual(vm.mem[0x40f1], 0x34)
        self.assertEqual(vm.mem[0x40f2], 0x12)
        self.assertEqual(vm.regs.PC, 1)

class ComplexTest(unittest.TestCase):
    pass

class ErrorTest(unittest.TestCase):
    def test_halt(self):
        vm = VM()
        vm.mem[0] = 0x76
        vm.execute_next()
        with self.assertRaises(VMError):
            vm.execute_next()
    
    def test_bad_instruction(self):
        vm = VM()
        vm.mem[0] = 0xff
        with self.assertRaises(VMError):
            vm.execute_next()
    
    def test_bad_address(self):
        vm = VM()
        # LDA, 0xffff
        vm.mem[0] = 0x3a
        vm.mem[1] = 0xff
        vm.mem[2] = 0xff
        with self.assertRaises(VMError):
            vm.execute_next()

unittest.main()
