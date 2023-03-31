#!/bin/bash
rm ./build/vm
mkdir -p build
gcc ./vm/vm.c ./vm/main.c -o ./build/vm
