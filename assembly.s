
.globl main
main:
  movq $42, -8(%rbp)
  negq -8(%rbp)
  movq -8(%rbp), %rdi
  callq print_int
