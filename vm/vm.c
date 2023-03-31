#include "vm.h"
#include <string.h>

const size_t VM_8085_RAM_SIZE = 64000;

int VM_8085_init(VM_8085 *vm, uint8_t *program, size_t prog_size) {
    vm->A = 0;
    vm->B = 0;
    vm->C = 0;
    vm->PC = 0;
    vm->memory = calloc(VM_8085_RAM_SIZE, sizeof(uint8_t));
    if(!vm->memory) return 1;
    vm->program = calloc(prog_size, sizeof(uint8_t));
    if(!vm->program) return 1;
    memcpy(vm->program, program, prog_size);
    vm->prog_size = prog_size;
    return 0;
}

void VM_8085_free(VM_8085 *vm) {
    free(vm->memory);
    free(vm->program);
}

int VM_8085_has_next(VM_8085 *vm) {
    return vm->PC < vm->prog_size;
}

int VM_8085_execute_next(VM_8085 *vm) {
    ++vm->PC;
    return 0;
}
