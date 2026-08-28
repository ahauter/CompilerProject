from Lint import (
    LInt, Module, Expr, Name, BinOp,
    Add, Sub, Mul, Div, Constant, UnOp, USub, Call
)
from x86 import *


class Assignment:
    def __init__(self, name, expr):
        if type(name) is not Name:
            raise ValueError("Wrong type for name! Must be a Name")
        if type(expr) is not Expr:
            raise ValueError("Wrong type for expr! Must be a expr")
        self.name = name
        self.expr = expr

    def __str__(self):
        if isinstance(self.name, Name):
            return f"{self.name.id} = {self.expr}"
        return f"{self.name} = {self.expr}"

    __repr__ = __str__


class LVar(LInt):
    def __init__(self):
        self.env = {}
        self.comp_env = {}

    def get_id(self):
        cur_id = "cur_id"
        if cur_id not in self.comp_env.keys():
            self.comp_env[cur_id] = -1
        self.comp_env[cur_id] += 1
        return f"tmp_{self.comp_env[cur_id]}"

    def interp(self, p):
        match p:
            case Module(body=body):
                for s in body:
                    self.interp_stmt(s)

    def interp_stmt(self, s):
        match s:
            case Assignment(name=Name(id=id), expr=Expr(expr=e)):
                self.env[id] = self.interp_exp(e)
            case _:
                return super().interp_stmt(s)

    def interp_exp(self, e):
        match e:
            case Name(id=id):
                return self.env[id]
            case _:
                return super().interp_exp(e)

    def rco_exp(self, exp, need_atomic):
        new_statements = []
        match exp:
            case BinOp(left=child1, op=op, right=child2):
                l = self.rco_exp(child1, True)
                r = self.rco_exp(child2, True)
                new_l = child1
                new_r = child2
                if len(l) > 0:
                    new_l = Name(l[-1].name)
                    new_statements.extend(l)
                if len(r) > 0:
                    new_r = Name(r[-1].name)
                    new_statements.extend(r)
                new_stmt = BinOp(new_l, op, new_r)
                if need_atomic:
                    new_stmt = Assignment(Name(self.get_id()), Expr(new_stmt))
                new_statements.append(new_stmt)
                return new_statements
            case Constant(value=value):
                return []
            case UnOp(op=USub(), right=const):
                constant = self.rco_exp(const, True)
                new_cnst = const
                if len(constant) > 0:
                    new_statements.extend(constant)
                    new_cnst = Name(constant[-1].name)
                new_stmt = UnOp(USub(), new_cnst)
                new_statements.append(new_stmt)
                return new_statements
            case Call(func=Name(id='input_int'), args=[]):
                return []

    def remove_complex_operands(self, module: Module):
        new_module = []
        for s in module.body:
            new_statements = []
            match s:
                case Assignment(name=Name(id=id), expr=Expr(expr=e)):
                    new_statements = self.rco_exp(e, False)
                    expression = e
                    if len(new_statements) > 0:
                        expression = new_statements.pop()
                    new_statements.append(
                        Assignment(Name(id), Expr(expression))
                    )
                case Expr(expr=Call(func=Name(id='print'), args=[Expr(expr=e)])):
                    new_statements = self.rco_exp(e, False)
                    expression = e
                    if len(new_statements) > 0:
                        expression = new_statements.pop()
                    new_statements.append(
                        Expr(Call(Name('print'), args=[Expr(expression)]))
                    )
                case Expr(expr=e):
                    new_statements = self.rco_exp(e, False)
                    expression = e
                    if len(new_statements) > 0:
                        expression = new_statements.pop()
                    new_statements.append(
                        Expr(expression)
                    )
                case _:
                    raise ValueError("Could not recognize expression")
            new_module.extend(new_statements)

        return new_module

    def select_instructions_exp(self, expr):
        instrs = []
        match expr:
            case BinOp(left=child2, op=Add(), right=Constant(value=const)):
                new_instrs, arg2 = self.select_instructions_exp(child2)
                instrs.extend(new_instrs)
                instrs.append(AddQ(Immediate(const), arg2))
                return (instrs, arg2)
            case BinOp(left=Constant(value=const), op=Add(), right=child2):
                new_instrs, arg2 = self.select_instructions_exp(child2)
                instrs.extend(new_instrs)
                instrs.append(AddQ(Immediate(const), arg2))
                return (instrs, arg2)
            case BinOp(left=child1, op=Add(), right=child2):
                new_instrs, arg1 = self.select_instructions_exp(child1)
                instrs.extend(new_instrs)
                new_instrs, arg2 = self.select_instructions_exp(child2)
                instrs.extend(new_instrs)
                instrs.append(AddQ(arg1, arg2))
                return (instrs, arg2)
            case BinOp(left=Constant(value=const), op=Sub(), right=child2):
                new_instrs, arg2 = self.select_instructions_exp(child2)
                instrs.extend(new_instrs)
                instrs.append(SubQ(Immediate(const), arg2))
                return (instrs, arg2)
            case BinOp(left=child2, op=Sub(), right=Constant(value=const)):
                new_instrs, arg2 = self.select_instructions_exp(child2)
                instrs.extend(new_instrs)
                instrs.append(SubQ(Immediate(const), arg2))
                return (instrs, arg2)
            case BinOp(left=child1, op=Sub(), right=child2):
                new_instrs, arg1 = self.select_instructions_exp(child1)
                instrs.extend(new_instrs)
                new_instrs, arg2 = self.select_instructions_exp(child2)
                instrs.extend(new_instrs)
                instrs.append(SubQ(arg1, arg2))
                return (instrs, arg2)
            case Constant(value=value):
                tmp = NameQ(self.get_id())
                return [Move(Immediate(value), tmp)], tmp
            case Name(id=id):
                return [], NameQ(id)
            case UnOp(op=USub(), right=expr):
                new_instrs, arg1 = self.select_instructions_exp(expr)
                instrs.extend(new_instrs)
                instrs.append(NegQ(arg1))
                return instrs, arg1
            case Call(func=Name(id='input_int'), args=[]):
                instrs.append(CallQ(NameQ("input_int"), None))
                return instrs, None
            case Call(func=Name(id='print'), args=[Expr(expr=e)]):
                new_instrs, arg1 = self.select_instructions_exp(e)
                instrs.extend(new_instrs)
                instrs.append(CallQ(NameQ("print"), arg1))
                return instrs, None
            case _:
                print("Expression not recognized")
                raise ValueError(
                    f"Expression cannot be translated into instruction: {expr}"
                )

    def select_instructions(self, module):
        # assuming we've already removed complex operands
        x86_instructions = []
        for s in module.body:
            match s:
                case Assignment(name=Name(id=id), expr=Expr(expr=e)):
                    exp_instructions, arg1 = self.select_instructions_exp(e)
                    x86_instructions.extend(exp_instructions)
                    x86_instructions.append(Move(arg1, NameQ(id)))
                case Expr(expr=e):
                    exp_instructions, arg1 = self.select_instructions_exp(e)
                    x86_instructions.extend(exp_instructions)
                case _:
                    print(type(s.name.id))
                    raise ValueError(f"Statement {s} not recognized!")
        return x86_instructions

    def compile(self, module):
        module = self.remove_complex_operands(module)
        x86_var_inst = self.select_instructions(module)
        x86_int_inst = self.assign_homes(x86_var_inst)
        x86_final_inst = self.patch_instructions(x86_int_inst)
        print(x86_final_inst)


if __name__ == "__main__":
    ast1_1 = Assignment(
        Name(id="variable1"),
        Expr(BinOp(Call(Name("input_int"), []), Add(), UnOp(USub(), Constant(8)))),
    )
    read = Call(Name("input_int"), [])
    prog1 = Expr(ast1_1)
    prog2 = Expr(BinOp(read, Sub(), UnOp(Add(), Constant(8))))

    prog3 = Module(
        [ast1_1, Expr(Call(Name("print"), [Expr(Name("variable1"))]))])

    comp = LVar()
    # comp.interp(prog3)  # requires interactive input, skipped for testing
    # Write tests for remove_complex_operands here

    def run_test(name, program):
        print(f"\n=== {name} ===")
        print("Before:")
        for stmt in program.body:
            print(f"  {stmt}")
        c = LVar()
        result = c.remove_complex_operands(program)
        print("After RCO:")
        for stmt in result:
            print(f"  {stmt}")
        try:
            x86_instrs = c.select_instructions(Module(result))
            print("After select_instructions:")
            for instr in x86_instrs:
                print(f"  {instr}")
            from x86 import Program, X86_var
            validator = X86_var()
            is_valid = validator.is_valid(Program(x86_instrs))
            print(f"Valid x86_var: {is_valid}")
        except Exception as e:
            print(f"ERROR during select_instructions: {type(e).__name__}: {e}")

    # Test 1: print with nested binop on the right
    test1 = Module([
        Expr(Call(Name("print"), [
            Expr(BinOp(Constant(1), Add(), BinOp(Constant(2), Add(), Constant(3))))
        ]))
    ])
    run_test("Test 1: print(1 + (2 + 3))", test1)

    # Test 2: assignment with nested binop on the left
    test2 = Module([
        Assignment(Name("x"), Expr(
            BinOp(BinOp(Constant(1), Add(), Constant(2)), Add(), Constant(3))
        ))
    ])
    run_test("Test 2: x = (1 + 2) + 3", test2)

    # Test 3: print with unary negation of nested expression
    test3 = Module([
        Expr(Call(Name("print"), [
            Expr(UnOp(USub(), BinOp(Constant(1), Add(), Constant(2))))
        ]))
    ])
    run_test("Test 3: print(-(1 + 2))", test3)
