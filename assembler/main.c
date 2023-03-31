#include "assembler.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

const size_t OUTPUT_BLOCK = 256;

size_t read_input(const char *file, char **buffer) {
    FILE *input = fopen(file, "r");
    if(!input) {
        fprintf(stderr, "Failed to open input file %s\n", file);
        exit(1);
    }
    fseek(input, 0, SEEK_END);
    size_t sz = ftell(input);
    rewind(input);
    *buffer = calloc(sz + 1, sizeof(char));
    if(*buffer == NULL) {
        fprintf(stderr, "Failed to read input file %s\n", file);
        exit(1);
    }
    fread(*buffer, sizeof(char), sz, input);
    (*buffer)[sz] = '\x00';
    fclose(input);
    return sz;
}

void write_output(const char* file, const uint8_t *buffer, size_t sz) {
    FILE *output = fopen(file, "wb");
    if(!output) {
        fprintf(stderr, "Failed to open output file %s\n", file);
        exit(1);
    }
    fwrite(buffer, sz, sizeof(uint8_t), output);
    fclose(output);
}

uint8_t * ASM_8085_assemble(char *program, size_t program_sz, size_t *code_sz);

int main(int argc, char **argv) {
    if(argc != 3) {
        fprintf(stderr, "Usage: %s [input] [output]\n", argv[0]);
        return 1;
    }
    // read input file
    char *input;
    size_t input_sz = read_input(argv[1], &input); 
    uint8_t *output;
    size_t output_sz;
    output = ASM_8085_assemble(input, input_sz, &output_sz);
    if(!output) {
        fprintf(stderr, "An error occured\n");
        return 1;
    }
    write_output(argv[2], output, output_sz);
    return 0;
}
