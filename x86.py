# bleh

REGISTERS = {
    "rsp": "rsp",
    "rbp": "rbp",
    "rax": "rax",
    "rbx": "rbx",
    "rcx": "rcx",
    "rdx": "rdx",
    "rsi": "rsi",
    "rdi": "rdi",
    "r8": "r8",
    "r9": "r9",
    "r10": "r10",
    "r11": "r11",
    "r12": "r12",
    "r13": "r13",
    "r14": "r14",
    "r15": "r15",
}


class AddQ:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"addq {self.arg1}, {self.arg2}"

    __repr__ = __str__


class SubQ:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"subq {self.arg1}, {self.arg2}"

    __repr__ = __str__


class NegQ:
    def __init__(self, arg1):
        self.arg1 = arg1

    def __str__(self):
        return f"negq {self.arg1}"

    __repr__ = __str__


class Move:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"movq {self.arg1}, {self.arg2}"

    __repr__ = __str__


class Push:
    def __init__(self, arg1):
        self.arg1 = arg1

    def __str__(self):
        return f"pushq {self.arg1}"

    __repr__ = __str__


class Pop:
    def __init__(self, arg1):
        self.arg1 = arg1

    def __str__(self):
        return f"popq {self.arg1}"

    __repr__ = __str__


class CallQ:
    def __init__(self, label, i):
        self.label = label
        self.i = i

    def __str__(self):
        if self.i is None:
            return f"callq {self.label}"
        return f"callq {self.label} {self.i}"

    __repr__ = __str__


class Jump:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f"jmp {self.label}"

    __repr__ = __str__


class Ret:
    def __str__(self):
        return "retq"

    __repr__ = __str__


class Register:
    def __init__(self, name):
        if name not in REGISTERS.keys():
            raise ValueError(f"Not a recognized register: {name}")
        self.name = name

    def __str__(self):
        return f"%{self.name}"

    __repr__ = __str__


class Immediate:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"${self.value}"

    __repr__ = __str__


class StackLocation:
    def __init__(self, register, value):
        self.register = register
        self.value = value

    def __str__(self):
        return f"{self.value}({self.register})"

    __repr__ = __str__


class Program:
    def __init__(self, instrs):
        self.instructions = instrs

    def __str__(self):
        return "\n".join(str(i) for i in self.instructions)

    __repr__ = __str__


class X86_int:
    def _is_reg(self, register):
        return register in REGISTERS.keys()

    def _is_arg(self, arg):
        match arg:
            case Immediate(value=_):
                return True
            case Register(name=name):
                return self._is_reg(name)
            case StackLocation(register=reg, value=_):
                return self._is_reg(reg.name)
            case _:
                return False

    def _is_instr(self, instr):
        match instr:
            case AddQ(arg1=a, arg2=b):
                return self._is_arg(a) and self._is_arg(b)
            case SubQ(arg1=a, arg2=b):
                return self._is_arg(a) and self._is_arg(b)
            case Move(arg1=a, arg2=b):
                return self._is_arg(a) and self._is_arg(b)
            case NegQ(arg1=a):
                return self._is_arg(a)
            case Push(arg1=a):
                return self._is_arg(a)
            case Pop(arg1=a):
                return self._is_arg(a)
            case Jump(label=_):
                return True
            case CallQ(label=NameQ(id=_), integer=_):
                return True
            case Ret():
                return True
            case _:
                return False

    def is_valid(self, program):
        is_valid = True
        for s in program.instructions:
            is_valid = is_valid and self._is_instr(s)
        return is_valid


class NameQ:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return f"{self.id}"

    __repr__ = __str__


class X86_var(X86_int):
    def _is_arg(self, arg):
        match arg:
            case NameQ(id=_):
                return True
            case _:
                return super()._is_arg(arg)


if __name__ == '__main__':
    def run_test(name, program, validator):
        print(f"\n=== {name} ===")
        print("Program:")
        print(program)
        print(f"Valid: {validator.is_valid(program)}")

    # ---- x86_int tests (no variables) ----
    x86_int_validator = X86_int()

    prog1_int = Program([
        Move(Immediate(5), Register("rax")),
        AddQ(Immediate(3), Register("rax")),
        Ret()
    ])
    run_test("x86_int Test 1: movq $5, %rax; addq $3, %rax; retq",
             prog1_int, x86_int_validator)

    prog2_int = Program([
        Push(Register("rbp")),
        Pop(Register("rbp")),
        Ret()
    ])
    run_test("x86_int Test 2: pushq %rbp; popq %rbp; retq",
             prog2_int, x86_int_validator)

    prog3_int = Program([
        Move(Immediate(10), Register("rax")),
        NegQ(Register("rax")),
        Ret()
    ])
    run_test("x86_int Test 3: movq $10, %rax; negq %rax; retq",
             prog3_int, x86_int_validator)

    prog4_int = Program([
        Move(Immediate(10), Register("rax")),
        SubQ(Immediate(3), Register("rax")),
        Ret()
    ])
    run_test("x86_int Test 4: movq $10, %rax; subq $3, %rax; retq",
             prog4_int, x86_int_validator)

    prog5_int = Program([
        Move(Immediate(42), StackLocation(Register("rbp"), -8)),
        Ret()
    ])
    run_test("x86_int Test 5: movq $42, -8(%rbp); retq",
             prog5_int, x86_int_validator)

    # ---- x86_var tests (with variables) ----
    x86_var_validator = X86_var()

    prog1_var = Program([
        Move(Immediate(5), NameQ("x")),
        Move(NameQ("x"), Register("rax")),
        Ret()
    ])
    run_test("x86_var Test 1: movq $5, x; movq x, %rax; retq",
             prog1_var, x86_var_validator)

    prog2_var = Program([
        Move(Immediate(10), NameQ("x")),
        AddQ(Immediate(5), NameQ("x")),
        Move(NameQ("x"), Register("rax")),
        Ret()
    ])
    run_test("x86_var Test 2: movq $10, x; addq $5, x; movq x, %rax; retq",
             prog2_var, x86_var_validator)

    prog3_var = Program([
        Move(Immediate(7), NameQ("x")),
        NegQ(NameQ("x")),
        Move(NameQ("x"), Register("rax")),
        Ret()
    ])
    run_test("x86_var Test 3: movq $7, x; negq x; movq x, %rax; retq",
             prog3_var, x86_var_validator)

    prog4_var = Program([
        Move(Immediate(1), NameQ("x")),
        AddQ(NameQ("x"), Register("rax")),
        Ret()
    ])
    run_test("x86_var Test 4: movq $1, x; addq x, %rax; retq",
             prog4_var, x86_var_validator)

    prog5_var = Program([
        Move(Immediate(20), NameQ("x")),
        SubQ(Immediate(5), NameQ("x")),
        Move(NameQ("x"), Register("rax")),
        Ret()
    ])
    run_test("x86_var Test 5: movq $20, x; subq $5, x; movq x, %rax; retq",
             prog5_var, x86_var_validator)
