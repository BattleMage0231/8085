#include "assembler.h"
#include <stdlib.h>
#include <string.h>

const size_t BLOCK_SIZE = 256;

const size_t MAX_INSTRUCTION_SIZE = 3;

static size_t line_cnt;

static char *input;
static size_t input_idx;
static size_t input_sz;

static uint8_t *output;
static size_t output_idx;
static size_t output_sz;

typedef struct Token {
    size_t start;
    size_t end;
    union {
        uint8_t value8;
        uint16_t value16;
    };
    int valid;
} Token;

// returns 1 if newline was detected
int skip_whitespace() {
    size_t old_line_cnt = line_cnt;
    while(input_idx < input_sz) {
        char cur = input[input_idx];
        switch(cur) {
            case '\n':
                ++line_cnt;
            case ' ':
            case '\t':
            case '\r':
                ++input_idx;
                break;
            case ';': {
                ++input_idx;
                while(input_idx < input_sz) {
                    if(input[input_idx] == '\n') {
                        break;
                    }
                    ++input_idx;
                }
                break;
            }
            default:
                return line_cnt != old_line_cnt;
        }
    }
    return line_cnt != old_line_cnt;
}

Token parse_string() {
    Token tok;
    tok.start = input_idx;
    while(input_idx < input_sz) {
        char cur = input[input_idx];
        if(cur < 'A' || cur > 'Z') break;
        ++input_idx;
    }
    tok.end = input_idx;
    tok.valid = 1;
    return tok;
}

int is_digit(char c) {
    return '0' <= c && c <= '9';
}

int is_hex_digit(char c) {
    return ('A' <= c && c <= 'F') || is_digit(c);
}

uint8_t hex_to_nib(char c) {
    if(is_digit(c)) {
        return (uint8_t) (c - '0');
    }
    return (uint8_t) (c - 'A') + 10;
}

Token parse_byte() {
    Token tok;
    tok.start = input_idx;
    uint8_t byte = 0;
    for(size_t i = 0; i < 2; ++i, ++input_idx) {
        char c = input[input_idx];
        if(!is_hex_digit(c)) {
            tok.valid = 0;
            return tok;
        }
        byte = (byte << 4) | hex_to_nib(c);
    }
    tok.value8 = byte;
    tok.end = input_idx;
    tok.valid = 1;
    return tok;
}

Token parse_two_bytes() {
    Token tok;
    tok.start = input_idx;
    uint16_t val = 0;
    for(size_t i = 0; i < 4; ++i, ++input_idx) {
        char c = input[input_idx];
        if(!is_hex_digit(c)) {
            tok.valid = 0;
            return tok;
        }
        val = (val << 4) | hex_to_nib(c);
    }
    tok.value16 = val;
    tok.end = input_idx;
    tok.valid = 1;
    return tok;
}

int tok_cmp(Token tok, char *str) {
    size_t len = tok.end - tok.start;
    return strncmp(input + tok.start, str, len);
}

#define EMIT(b) output[output_idx++] = (b)

int parse_instruction() {
    Token op = parse_string();
    if(!op.valid) return 1;
    if(tok_cmp(op, "NOP") == 0) {
        EMIT(0x00);
        return 0;
    } else if(tok_cmp(op, "MVI") == 0) {
        if(skip_whitespace()) return 1;
        Token reg = parse_string();
        if(!reg.valid) return 1;
        if(tok_cmp(reg, "A") == 0) {
            EMIT(0x3e);
        } else if(tok_cmp(reg, "B") == 0) {
            EMIT(0x06);
        } else if(tok_cmp(reg, "C") == 0) {
            EMIT(0x0e);
        } else {
            return 1;
        }
        if(skip_whitespace()) return 1;
        if(input[input_idx] != ',') return 1;
        ++input_idx;
        if(skip_whitespace()) return 1;
        Token byte = parse_byte();
        if(!byte.valid) return 1;
        EMIT(byte.value8);
        return 0;
    } else if(tok_cmp(op, "STA") == 0) {
        EMIT(0x32);
        if(skip_whitespace()) return 1;
        Token addr = parse_two_bytes();
        if(!addr.valid) return 1;
        EMIT((uint8_t) ((addr.value16 & 0xFF00) >> 8));
        EMIT((uint8_t) ((addr.value16 & 0x00FF)));
        return 0;
    } else if(tok_cmp(op, "LDA") == 0) {
        EMIT(0x3a);
        if(skip_whitespace()) return 1;
        Token addr = parse_two_bytes();
        if(!addr.valid) return 1;
        EMIT((uint8_t) ((addr.value16 & 0xFF00) >> 8));
        EMIT((uint8_t) ((addr.value16 & 0x00FF)));
        return 0;
    } else if(tok_cmp(op, "HLT") == 0) {
        EMIT(0x76);
        return 0;
    } else if(tok_cmp(op, "ADI") == 0) {
        EMIT(0xc6);
        if(skip_whitespace()) return 1;
        Token byte = parse_byte();
        if(!byte.valid) return 1;
        EMIT(byte.value8);
        return 0;
    } else {
        return 1;
    }
}

uint8_t * ASM_8085_assemble(char *program, size_t program_sz, size_t *code_sz) {
    line_cnt = 0;
    input = program;
    input_idx = 0;
    input_sz = program_sz;
    output = malloc(BLOCK_SIZE * sizeof(uint8_t));
    output_idx = 0;
    output_sz = BLOCK_SIZE;
    while(input_idx < input_sz) {
        if(output_idx + MAX_INSTRUCTION_SIZE >= output_sz) {
            output_sz += BLOCK_SIZE;
            if(!realloc(output, sizeof(uint8_t) * output_sz)) {
                free(output);
                *code_sz = 0;
                return NULL;
            }
        }
        if(parse_instruction()) {
            free(output);
            *code_sz = 0;
            return NULL;
        }
        skip_whitespace();
    }
    *code_sz = output_idx;
    return output;
}
