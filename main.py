class Constant:
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value


class Module:
    def __init__(self, body):
        self.body = body


class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op


class UnOp:
    def __init__(self, op, right):
        self.op = op
        self.right = right


class USub:
    pass


class Add:
    pass


class Sub:
    pass


class Mul:
    pass


class Div:
    pass


class Call:
    def __init__(self, func, args):
        self.func = func
        self.args = args


class Name:
    def __init__(self, id):
        self.id = id


class Expr:
    def __init__(self, expr):
        self.expr = expr


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
            return False


def is_stmt(s):
    match s:
        case Expr(expr=Call(func=Name('print'), args=[e])):
            return is_exp(e)
        case Expr(expr=e):
            return is_exp(e)
        case _:
            return False


def is_Lint(p):
    match p:
        case Module(body=body):
            return all([is_stmt(s) for s in body])
        case _:
            return False


def interp_exp(e):
    match e:
        case BinOp(left=child1, op=Add(), right=child2):
            l = interp_exp(child1)
            r = interp_exp(child2)
            return l + r
        case BinOp(left=child1, op=Sub(), right=child2):
            l = interp_exp(child1)
            r = interp_exp(child2)
            return l - r
        case BinOp(left=child1, op=Mul(), right=child2):
            l = interp_exp(child1)
            r = interp_exp(child2)
            return l * r
        case BinOp(left=child1, op=Div(), right=child2):
            l = interp_exp(child1)
            r = interp_exp(child2)
            return l / r
        case Constant(value=value):
            return value
        case UnOp(op=USub(), right=const):
            return -1 * interp_exp(const)
        case Call(func=Name(id='input_int'), args=[]):
            return int(input())


def interp_stmt(s):
    match s:
        case Expr(expr=Call(func=Name(id='print'), args=[Expr(expr=e)])):
            print(interp_exp(e))
        case Expr(expr=e):
            interp_exp(e)


def interp_Lint(p):
    match p:
        case Module(body=body):
            for s in body:
                interp_stmt(s)


ast1_1 = BinOp(Call(Name("input_int"), []), Add(), UnOp(USub(), Constant(8)))
read = Call(Name("input_int"), [])
print(is_Lint(Module([Expr(ast1_1)])))
print(is_Lint(Module([
    Expr(BinOp(read, Sub(), UnOp(Add(), Constant(8))))
])))
interp_Lint(Module([Expr(Call(Name("print"), [Expr(ast1_1)]))]))
