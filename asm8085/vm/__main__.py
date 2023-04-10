import unittest
from util import VMError, Registers, Flags
from vm import VM

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

class ArithmeticTest(unittest.TestCase):
    def test_add(self):
        vm = VM()
        vm.mem[0] = 0x82 # ADD D
        vm.regs.A = 0x2e
        vm.regs.D = 0x6c
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x9a)
        self.assertEqual(vm.flags.as_byte(), 0x84)
        self.assertEqual(vm.regs.PC, 1)

    def test_adi(self):
        vm = VM()
        # ADI 66
        vm.mem[0] = 0xc6
        vm.mem[1] = 0x42
        vm.regs.A = 0x14
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x56)
        self.assertEqual(vm.flags.as_byte(), 0x04)
        self.assertEqual(vm.regs.PC, 2)

    def test_adc(self):
        vm = VM()
        vm.mem[0] = 0x89 # ADC C
        vm.regs.A = 0x42
        vm.regs.C = 0x3d
        vm.flags.CY = 1
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x80)
        self.assertEqual(vm.flags.as_byte(), 0x80)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_adc_max(self):
        vm = VM()
        vm.mem[0] = 0x89 # ADC C
        vm.regs.A = 0x42
        vm.regs.C = 0xff
        vm.flags.CY = 1
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x42)
        self.assertEqual(vm.flags.as_byte(), 0x05)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_aci(self):
        vm = VM()
        # ACI 42
        vm.mem[0] = 0xce
        vm.mem[1] = 0x42
        vm.regs.A = 0x14
        vm.flags.CY = 1
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x57)
        self.assertEqual(vm.flags.as_byte(), 0x00)
        self.assertEqual(vm.regs.PC, 2)
    
    def test_sub(self):
        vm = VM()
        vm.mem[0] = 0x97 # SUB A
        vm.regs.A = 0x3e
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x00)
        self.assertEqual(vm.flags.as_byte(), 0x44)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_sub_zero(self):
        vm = VM()
        vm.mem[0] = 0x97 # SUB A
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x00)
        self.assertEqual(vm.flags.as_byte(), 0x44)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_sui(self):
        vm = VM()
        # SUI 01
        vm.mem[0] = 0xd6
        vm.mem[1] = 0x01
        vm.regs.A = 0x09
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x08)
        self.assertEqual(vm.flags.as_byte(), 0x00)
        self.assertEqual(vm.regs.PC, 2)
    
    def test_sbb(self):
        vm = VM()
        vm.mem[0] = 0x98 # SBB B
        vm.regs.A = 0x04
        vm.regs.B = 0x02
        vm.flags.CY = 1
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x01)
        self.assertEqual(vm.flags.as_byte(), 0x00)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_sbb_max(self):
        vm = VM()
        vm.mem[0] = 0x98 # SBB B
        vm.regs.A = 0x12
        vm.regs.B = 0xff
        vm.flags.CY = 1
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x12)
        self.assertEqual(vm.flags.as_byte(), 0x05)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_sbi(self):
        vm = VM()
        # SBI 02
        vm.mem[0] = 0xde
        vm.mem[1] = 0x02
        vm.regs.A = 0x04
        vm.flags.CY = 1
        vm.execute_next()
        self.assertEqual(vm.regs.A, 0x01)
        self.assertEqual(vm.flags.as_byte(), 0x00)
        self.assertEqual(vm.regs.PC, 2)

    def test_inr(self):
        vm = VM()
        vm.mem[0] = 0x0c # INR C
        vm.regs.C = 0x99
        vm.execute_next()
        self.assertEqual(vm.regs.C, 0x9a)
        self.assertEqual(vm.flags.as_byte(), 0x84)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_dcr(self):
        vm = VM()
        vm.mem[0] = 0x25 # DCR H
        vm.regs.H = 0x00
        vm.flags.CY = 1
        vm.execute_next()
        self.assertEqual(vm.regs.H, 0xff)
        self.assertEqual(vm.flags.as_byte(), 0x85)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_inx(self):
        vm = VM()
        vm.mem[0] = 0x13 # INX DE
        vm.regs.DE = 0x01ff
        vm.execute_next()
        self.assertEqual(vm.regs.DE, 0x0200)
        self.assertEqual(vm.flags.as_byte(), 0x00)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_dcx(self):
        vm = VM()
        vm.mem[0] = 0x2b # DCX HL
        vm.regs.HL = 0x9800
        vm.execute_next()
        self.assertEqual(vm.regs.HL, 0x97ff)
        self.assertEqual(vm.flags.as_byte(), 0x00)
        self.assertEqual(vm.regs.PC, 1)
    
    def test_dad(self):
        vm = VM()
        vm.mem[0] = 0x39 # DAD SP
        vm.regs.HL = 0x1234
        vm.regs.SP = 0xffff
        vm.execute_next()
        self.assertEqual(vm.regs.HL, 0x1233)
        self.assertEqual(vm.flags.as_byte(), 0x01)
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
