#pragma once

#include <stddef.h>
#include <stdint.h>

uint8_t * ASM_8085_assemble(char *program, size_t program_sz, size_t *code_sz);
