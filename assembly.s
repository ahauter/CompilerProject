
.globl main
main:
    movq $12, %rdi
    callq print_int
    movq $0, %rax
    retq
