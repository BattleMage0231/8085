#!/bin/bash
rm ./build/disas
mkdir -p build
gcc ./disassembler/disas.c -o ./build/disas
