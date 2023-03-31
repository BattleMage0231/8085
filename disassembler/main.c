#include <stdint.h>
#include <stdio.h>

const size_t MAX_INSTRUCTION_SIZE = 3;

void print_bytes(uint8_t *buffer, size_t index, size_t count) {
    for(size_t i = 0; i < MAX_INSTRUCTION_SIZE; ++i) {
        if(i < count) {
            printf("%02x ", buffer[index + i]);
        } else {
            printf("   ");
        }
    }
}

#define PRINT(count) print_bytes(buffer, index, count)

size_t disassemble_instruction(uint8_t *buffer, size_t index) {
    uint8_t opcode = buffer[index];
    uint8_t arg1 = buffer[index + 1];
    uint8_t arg2 = buffer[index + 2];
    uint8_t arg3 = buffer[index + 3];
    switch(opcode) {
        case 0x00:
            PRINT(1); printf("NOP\n"); return 1;
        case 0x06:
            PRINT(2); printf("MVI B, %02x\n", arg1); return 2;
        case 0x0e:
            PRINT(2); printf("MVI C, %02x\n", arg1); return 2;
        case 0x32:
            PRINT(3); printf("STA %02x%02x\n", arg1, arg2); return 3;
        case 0x3a:
            PRINT(3); printf("LDA %02x%02x\n", arg1, arg2); return 3;
        case 0x3e:
            PRINT(2); printf("MVI A, %02x\n", arg1); return 2;
        case 0x76:
            PRINT(1); printf("HLT\n"); return 1;
        case 0xc6:
            PRINT(1); printf("ADI %02x\n", arg1); return 2;
        default:
            PRINT(1); printf("Unknown Instruction\n"); return 1;
    }
}

#undef PRINT

int main(int argc, char **argv) {
    if(argc == 1) {
        fprintf(stderr, "Usage: %s [file]\n", argv[0]);
        return 1;
    }
    FILE *file = fopen(argv[1], "rb");
    if(!file) {
        fprintf(stderr, "Failed to open file %s\n", argv[1]);
        return 1;
    }
    // get the size
    fseek(file, 0, SEEK_END);
    size_t sz = ftell(file);
    rewind(file);
    // read content into buffer
    uint8_t buffer[sz + 3];
    fread(buffer, sizeof(uint8_t), sz, file);
    fclose(file);
    // disassemble each instruction
    size_t index = 0;
    while(index < sz) {
        index += disassemble_instruction(buffer, index);
    }
    return 0;
}
