
.globl main
main:
  movq $1, -8(%rbp)
  addq $2, -8(%rbp)
  movq -8(%rbp), -16(%rbp)
  negq -16(%rbp)
  movq -16(%rbp), %rdi
  callq print_int
