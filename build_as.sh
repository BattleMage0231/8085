#!/bin/bash
rm ./build/as
mkdir -p build
gcc ./assembler/assembler.c ./assembler/main.c -o ./build/as -g
