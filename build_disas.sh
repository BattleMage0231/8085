#!/bin/bash
rm ./build/disas
mkdir -p build
gcc ./disassembler/main.c -o ./build/disas
