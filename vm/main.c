#include "vm.h"
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if(argc != 2) {
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
    unsigned char buffer[sz + 3];
    fread(buffer, sizeof(unsigned char), sz, file);
    fclose(file);
    // run the VM
    VM_8085 vm;
    if(VM_8085_init(&vm)) {
        fprintf(stderr, "Failed to initialize VM\n");
        return 1;
    }
    memcpy(vm.memory, buffer, sz);
    //vm.memory[0x23d4] = 0xff;
    while(!VM_8085_finished(&vm)) {
        if(VM_8085_execute_next(&vm)) {
            fprintf(stderr, "Failed to execute instruction\n");
            return 1;
        }
        //printf("DEBUG: %02x %02x\n", vm.memory[0x23d4], vm.memory[0xaa30]);
    }
    VM_8085_free(&vm);
    return 0;
}
