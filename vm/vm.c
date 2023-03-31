#include "vm.h"

const size_t VM_8085_RAM_SIZE = 64000;

int VM_8085_init(VM_8085 *vm) {
    vm->PC = 0;
    vm->memory = calloc(VM_8085_RAM_SIZE, sizeof(uint8_t));
    if(!vm->memory) return 1;
    vm->halted = 0;
    return 0;
}

void VM_8085_free(VM_8085 *vm) {
    free(vm->memory);
}

int VM_8085_finished(VM_8085 *vm) {
    return vm->halted;
}

#define CONCAT16(a, b) (((uint16_t) a << 8) | b)

int VM_8085_execute_next(VM_8085 *vm) {
    if(vm->halted) return 0;
    uint8_t opcode = vm->memory[vm->PC];
    uint8_t arg1 = vm->memory[vm->PC + 1];
    uint8_t arg2 = vm->memory[vm->PC + 2];
    uint8_t arg3 = vm->memory[vm->PC + 3];
    switch(opcode) {
        case 0x00: // NOP
            vm->PC += 1; return 0;
        case 0x06: // MVI B, arg1
            vm->B = arg1;
            vm->PC += 2; return 0;
        case 0x0e: // MVI C, arg1
            vm->C = arg1;
            vm->PC += 2; return 0;
        case 0x32: { // STA arg1arg2
            uint16_t addr = CONCAT16(arg1, arg2);
            vm->memory[addr] = vm->A;
            vm->PC += 3; return 0;
        }
        case 0x3a: { // LDA arg1arg2
            uint16_t addr = CONCAT16(arg1, arg2);
            vm->A = vm->memory[addr];
            vm->PC += 3; return 0;
        }
        case 0x3e: // MVI A, arg1
            vm->A = arg1;
            vm->PC += 2; return 0;
        case 0x76: // HLT
            vm->halted = 1;
            vm->PC += 1; return 0;
        case 0xc6: // ADI arg1
            vm->A += arg1;
            vm->PC += 2; return 0;
        default:
            return 1;
    }
}
