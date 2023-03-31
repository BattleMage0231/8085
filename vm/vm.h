#pragma once

#include <stdint.h>
#include <stdlib.h>

extern const size_t VM_8085_RAM_SIZE;

typedef struct VM_8085 {
    // registers
    uint8_t A;
    uint8_t B;
    uint8_t C;
    uint16_t PC;
    // ram
    uint8_t *memory;
    // rom (code)
    uint8_t *program;
    size_t prog_size;
} VM_8085;

int VM_8085_init(VM_8085 *vm, uint8_t *program, size_t prog_size);
void VM_8085_free(VM_8085 *vm);

int VM_8085_has_next(VM_8085 *vm);
int VM_8085_execute_next(VM_8085 *vm);
