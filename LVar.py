class Constant:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"{self.value}"


class Module:
    def __init__(self, body):
        self.body = body

    def __str__(self):
        return f"{self.body}"


class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        return f"{self.left}{self.op}{self.right}"


class UnOp:
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def __str__(self):
        return f"{self.op}{self.right}"


class USub:
    def __str__(self):
        return f"-"


class Add:
    def __str__(self):
        return f"+"


class Sub:
    def __str__(self):
        return f"-"


class Mul:
    def __str__(self):
        return f"*"


class Div:
    def __str__(self):
        return f"/"


class Call:
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __str__(self):
        return f"{self.func}({self.args})"


class Name:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return f"{self.id}"


class Expr:
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"{self.expr}"


class InterpLint:
    def interp(self, p):
        match p:
            case Module(body=body):
                for s in body:
                    self.interp_stmt(s)

    def interp_stmt(self, s):
        match s:
            case Expr(expr=Call(func=Name(id='print'), args=[Expr(expr=e)])):
                print(self.interp_exp(e))
            case Expr(expr=e):
                self.interp_exp(e)

    def interp_exp(self, e):
        match e:
            case BinOp(left=child1, op=Add(), right=child2):
                l = self.interp_exp(child1)
                r = self.interp_exp(child2)
                return l + r
            case BinOp(left=child1, op=Sub(), right=child2):
                l = self.interp_exp(child1)
                r = self.interp_exp(child2)
                return l - r
            case BinOp(left=child1, op=Mul(), right=child2):
                l = self.interp_exp(child1)
                r = self.interp_exp(child2)
                return l * r
            case BinOp(left=child1, op=Div(), right=child2):
                l = self.interp_exp(child1)
                r = self.interp_exp(child2)
                return l / r
            case Constant(value=value):
                return value
            case UnOp(op=USub(), right=const):
                return -1 * self.interp_exp(const)
            case Call(func=Name(id='input_int'), args=[]):
                return int(input())


env = {}


class Assignment:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def __str__(self):
        return f"{self.name.id} = {self.expr}"


class InterpLVar(InterpLint):
    def __init__(self):
        self.env = {}

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


def is_exp(line: str):
    match line:
        case BinOp(left=child1, op=Add(), right=child2):
            return is_exp(child1) and is_exp(child2)
        case BinOp(left=child1, op=Sub(), right=child2):
            return is_exp(child1) and is_exp(child2)
        case BinOp(left=child1, op=Mul(), right=child2):
            return is_exp(child1) and is_exp(child2)
        case BinOp(left=child1, op=Div(), right=child2):
            return is_exp(child1) and is_exp(child2)
        case Constant(value=value):
            return True
        case UnOp(op=USub(), right=const):
            return is_exp(const)
        case Call(func=Name(id='input_int'), args=[]):
            return True
        case _:
            print("Expression not recognized")
            print(line)
            return False


def is_stmt(s):
    match s:
        case Expr(expr=Call(func=Name(id='print'), args=[Expr(expr=e)])):
            return is_exp(e)
        case Expr(expr=e):
            return is_exp(e)
        case _:
            print("Statement not recognized")
            return False


def is_Lint(p):
    match p:
        case Module(body=body):
            return all([is_stmt(s) for s in body])
        case _:
            print("Module not recognized")
            return False


def pe_neg(r):
    match r:
        case Constant(value=n):
            return Constant(-1 * n)
        case _:
            return UnOp(USub(), r)


def pe_add(r1, r2):
    match (r1, r2):
        case Constant(value=r1), Constant(value=r2):
            return Constant(r1 + r2)
        case _:
            return BinOp(r1, Add(), r2)


def pe_sub(r1, r2):
    match (r1, r2):
        case Constant(value=r1), Constant(value=r2):
            return Constant(r1 - r2)
        case _:
            return BinOp(r1, Sub(), r2)


def pe_mul(r1, r2):
    match (r1, r2):
        case Constant(value=r1), Constant(value=r2):
            return Constant(r1 * r2)
        case _:
            return BinOp(r1, Mul(), r2)


def pe_div(r1, r2):
    match (r1, r2):
        case Constant(value=r1), Constant(value=r2):
            return Constant(r1 / r2)
        case _:
            return BinOp(r1, Div(), r2)


def pe_exp(e):
    match e:
        case BinOp(left=l1, op=Add(), right=r1):
            return pe_add(pe_exp(l1), pe_exp(r1))
        case BinOp(left=l1, op=Sub(), right=r1):
            return pe_sub(pe_exp(l1), pe_exp(r1))
        case BinOp(left=l1, op=Mul(), right=r1):
            return pe_mul(pe_exp(l1), pe_exp(r1))
        case BinOp(left=l1, op=Div(), right=r1):
            return pe_div(pe_exp(l1), pe_exp(r1))
        case UnOp(op=USub(), right=r):
            return pe_neg(pe_exp(r))
        case Constant(value=_):
            return e
        case Call(func=Name(id="input_int"), args=[]):
            return e
        case _:
            print("OOPS")


def pe_stmt(s):
    match s:
        case Expr(expr=Call(func=Name(id="print"), args=[Expr(expr=e)])):
            return Expr(expr=Call(func=Name(id="print"), args=[Expr(pe_exp(e))]))
        case Expr(expr=value):
            return Expr(expr=pe_exp(value))


def pe_P_int(p):
    match p:
        case Module(body=body):
            new_body = [pe_stmt(s) for s in body]
            return Module(new_body)


ast1_1 = Assignment(
    Name(id="variable1"),
    Expr(BinOp(Call(Name("input_int"), []), Add(), UnOp(USub(), Constant(8)))),
)
read = Call(Name("input_int"), [])
prog1 = Expr(ast1_1)
prog2 = Expr(BinOp(read, Sub(), UnOp(Add(), Constant(8))))

prog3 = Module([ast1_1, Expr(Call(Name("print"), [Expr(Name("variable1"))]))])

print(is_Lint(prog3))
comp = InterpLVar()
comp.interp(prog3)
