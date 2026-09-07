from tokenizer.token import Token, Number, CharacterSet, tokenize, TokenLoc


class NewLine(CharacterSet):
    def __init__(self):
        super().__init__("\n")


class Constant:
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __str__(self):
        return f"{self.value}"

    __repr__ = __str__


class Module:
    def __init__(self, body):
        self.body = body

    def __str__(self):
        return "\n".join(str(s) for s in self.body)

    __repr__ = __str__


class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    __repr__ = __str__


class UnOp:
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def __str__(self):
        return f"({self.op}{self.right})"

    __repr__ = __str__


class USub(Token):
    def __str__(self):
        return f"-"

    __repr__ = __str__

    def is_valid_subtoken(self, c):
        return c == self.__str__()

    def is_valid_token(self, s):
        return c == self.__str__()


class Add(Token):
    def __str__(self):
        return f"+"

    __repr__ = __str__

    def is_valid_subtoken(self, c):
        return c == self.__str__()

    def is_valid_token(self, s):
        return s == self.__str__()


class Sub(Token):
    def __str__(self):
        return f"-"

    __repr__ = __str__

    def is_valid_subtoken(self, c):
        return c == self.__str__()

    def is_valid_token(self, s):
        return s == self.__str__()


class Mul(Token):
    def __str__(self):
        return f"*"

    __repr__ = __str__

    def is_valid_subtoken(self, c):
        return c == self.__str__()

    def is_valid_token(self, s):
        return s == self.__str__()


class Div(Token):
    def __str__(self):
        return f"/"

    __repr__ = __str__

    def is_valid_subtoken(self, c):
        return c == self.__str__()

    def is_valid_token(self, s):
        return s == self.__str__()


class Call:
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __str__(self):
        return f"{self.func}({', '.join(str(a) for a in self.args)})"

    __repr__ = __str__


class Identifier(CharacterSet):
    def __init__(self):
        valid = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        super().__init__(*[v for v in valid])

    def __str__(self):
        return "Identifier"


class Name(CharacterSet):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return f"{self.id}"

    __repr__ = __str__


class Expr:
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"{self.expr}"

    __repr__ = __str__


class LInt():
    def tokens(self):
        return [Add(), Sub(), Number(), Identifier(), NewLine()]

    def tokenize(self, corpus):
        return tokenize(corpus, self.tokens())

    def full_reduce(self, token_stream):
        result = Module([])
        token_stack = [None]
        for next_token in token_stream:
            result, token_stack = self.reduce(result, token_stack, next_token)
        match token_stack:
            case [Expr()]:
                result.body.append(token_stack[0])
        return result

    def reduce(self, result, token_stack, next_token):
        token_stack.append(next_token)
        match token_stack:
            case [None, TokenLoc(t=Number())]:
                value = token_stack[-1].text()
                token_stack = [Expr(Constant(int(value)))]
            case [None, TokenLoc(t=Sub())]:
                token_stack = [UnOp(Sub(), None)]
            case [UnOp(op=op, right=None), TokenLoc(t=Number())]:
                value = int(token_stack[-1].text())
                token_stack = [Expr(UnOp(op=op, right=Constant(value)))]
            case [Expr(), TokenLoc(t=Add())]:
                token_stack = [
                    BinOp(left=token_stack[0], op=Add(), right=None)
                ]
            case [Expr(), TokenLoc(t=Sub())]:
                token_stack = [
                    BinOp(left=token_stack[0], op=Sub(), right=None)
                ]
            case [BinOp(right=None), TokenLoc(t=Number())]:
                bo = token_stack[0]
                next_token = token_stack[1]
                bo.right = Expr(Constant(value=int(next_token.text())))
                token_stack = [Expr(bo)]
            case [BinOp(right=None), TokenLoc(t=Sub())]:
                bo = token_stack[0]
                bo.right = UnOp(op=USub(), right=None)
                token_stack = [bo]
            case [BinOp(right=UnOp(op=op, right=None)), TokenLoc(t=Number())]:
                bo = token_stack[0]
                next_token = token_stack[1]
                num = int(next_token.text())
                bo.right = UnOp(op=op, right=num)
            case [Expr(), NewLine()]:
                expr = token_stack[0]
                token_stack = [None]
                result.body.append(expr)
            case _:
                pass
        return result, token_stack

    def parse(self, corpus):
        return self.full_reduce(self.tokenize(corpus))

    def is_exp(self, line: str):
        match line:
            case BinOp(left=child1, op=Add(), right=child2):
                return self.is_exp(child1) and self.is_exp(child2)
            case BinOp(left=child1, op=Sub(), right=child2):
                return self.is_exp(child1) and self.is_exp(child2)
            case BinOp(left=child1, op=Mul(), right=child2):
                return self.is_exp(child1) and self.is_exp(child2)
            case BinOp(left=child1, op=Div(), right=child2):
                return self.is_exp(child1) and self.is_exp(child2)
            case Constant(value=value):
                return True
            case UnOp(op=USub(), right=const):
                return self.is_exp(const)
            case Call(func=Name(id='input_int'), args=[]):
                return True
            case _:
                print("Expression not recognized")
                print(line)
                return False

    def is_stmt(self, s):
        match s:
            case Expr(expr=Call(func=Name(id='print'), args=[Expr(expr=e)])):
                return self.is_exp(e)
            case Expr(expr=e):
                return self.is_exp(e)
            case _:
                print("Statement not recognized")
                return False

    def is_Lint(self, p):
        match p:
            case Module(body=body):
                return all([self.is_stmt(s) for s in body])
            case _:
                print("Module not recognized")
                return False

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

    def interp_stmt(self, s):
        match s:
            case Expr(expr=Call(func=Name(id='print'), args=[Expr(expr=e)])):
                print(self.interp_exp(e))
            case Expr(expr=e):
                self.interp_exp(e)

    def interp(self, p):
        match p:
            case Module(body=body):
                for s in body:
                    self.interp_stmt(s)

    def pe_neg(self, r):
        match r:
            case Constant(value=n):
                return Constant(-1 * n)
            case _:
                return UnOp(USub(), r)

    def pe_add(self, r1, r2):
        match (r1, r2):
            case Constant(value=r1), Constant(value=r2):
                return Constant(r1 + r2)
            case _:
                return BinOp(r1, Add(), r2)

    def pe_sub(self, r1, r2):
        match (r1, r2):
            case Constant(value=r1), Constant(value=r2):
                return Constant(r1 - r2)
            case _:
                return BinOp(r1, Sub(), r2)

    def pe_mul(self, r1, r2):
        match (r1, r2):
            case Constant(value=r1), Constant(value=r2):
                return Constant(r1 * r2)
            case _:
                return BinOp(r1, Mul(), r2)

    def pe_div(self, r1, r2):
        match (r1, r2):
            case Constant(value=r1), Constant(value=r2):
                return Constant(r1 / r2)
            case _:
                return BinOp(r1, Div(), r2)

    def pe_exp(self, e):
        match e:
            case BinOp(left=l1, op=Add(), right=r1):
                return self.pe_add(self.pe_exp(l1), self.pe_exp(r1))
            case BinOp(left=l1, op=Sub(), right=r1):
                return self.pe_sub(self.pe_exp(l1), self.pe_exp(r1))
            case BinOp(left=l1, op=Mul(), right=r1):
                return self.pe_mul(self.pe_exp(l1), self.pe_exp(r1))
            case BinOp(left=l1, op=Div(), right=r1):
                return self.pe_div(self.pe_exp(l1), self.pe_exp(r1))
            case UnOp(op=USub(), right=r):
                return self.pe_neg(self.pe_exp(r))
            case Constant(value=_):
                return e
            case Call(func=Name(id="input_int"), args=[]):
                return e
            case _:
                print("OOPS")

    def pe_stmt(self, s):
        match s:
            case Expr(expr=Call(func=Name(id="print"), args=[Expr(expr=e)])):
                return Expr(expr=Call(func=Name(id="print"), args=[Expr(self.pe_exp(e))]))
            case Expr(expr=value):
                return Expr(expr=self.pe_exp(value))

    def pe_P_int(self, p):
        match p:
            case Module(body=body):
                new_body = [self.pe_stmt(s) for s in body]
                return Module(new_body)


if __name__ == "__main__":
    ast1_1 = BinOp(Call(Name("input_int"), []),
                   Add(), UnOp(USub(), Constant(8)))
    read = Call(Name("input_int"), [])
    prog1 = Expr(ast1_1)
    prog2 = Expr(BinOp(read, Sub(), UnOp(Add(), Constant(8))))

    prog3 = Module([Expr(Call(Name("print"), [Expr(ast1_1)]))])
    def print_prog(e): return Module([Expr(Call(Name("print"), [e]))])

    interp = LInt()
    print(interp.is_Lint(Module([prog1])))
    print(interp.is_Lint(prog3))
    pe_prog1 = interp.pe_P_int(prog3)
    # pe_prog2 = pe_P_int(print_prog(prog2))
    # interp.interp(print_prog(prog1))
    # print(pe_prog1.body[0].expr.args[0].expr)
    # interp.interp(pe_prog1)

    c = "1234-123487"
    corpus = "1234-123487+134702-1381234"
    for token in interp.tokenize(corpus):
        print(token)
    print(interp.parse(corpus))
