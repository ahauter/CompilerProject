from abc import ABC, abstractclassmethod
from typing import List


class Token(ABC):
    @abstractclassmethod
    def is_valid_subtoken(self, c):
        pass

    @abstractclassmethod
    def is_valid_token(self, s):
        pass

    def get_full(self, s: str, start: int):
        for i in range(start, len(s)):
            if not self.is_valid_subtoken(s[start:i]):
                return i - 1
        return len(s)


class WordList(Token):
    def __init__(self, *args):
        self.tokens = [s for s in args if type(s) is str]

    def is_valid_token(self, s):
        return s in self.tokens

    def is_valid_subtoken(self, s):
        return any([s in token for token in self.tokens])

    def __str__(self):
        return "WordList"


class CharacterSet(Token):
    """
    given a set of characters, captures everything that only contains those characters
    e.g. {'1', '2', '0' } => "121" and "1200" from 12131200
    """

    def __init__(self, *args):
        self.characters = [c for c in args if type(c) is str and len(c) == 1]

    def is_valid_token(self, s: str):
        return all([c in self.characters for c in s])

    def is_valid_subtoken(self, s: str):
        return all([c in self.characters for c in s])

    def __str__(self):
        return "CharacterSet"


class Number(CharacterSet):
    """
    Any string that is a number e.g. all characters are digits
    """

    def __init__(self):
        super().__init__("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

    def __str__(self):
        return "Number"


class Add(CharacterSet):
    """
    Any string that is a number e.g. all characters are digits
    """

    def __init__(self):
        super().__init__("+")

    def __str__(self):
        return "Add"


class Sub(CharacterSet):
    """
    Any string that is a number e.g. all characters are digits
    """

    def __init__(self):
        super().__init__("-")

    def __str__(self):
        return "Sub"


class TokenSet(Token):
    def __init__(self, *args):
        self.tokens = [a for a in args if type(a) is Token]

    def is_valid_token(self, s):
        return any([t.is_valid_token(s) for t in self.tokens])

    def is_valid_subtoken(self, s):
        return any([t.is_valid_subtoken(s) for t in self.tokens])

    def __str__(self):
        return "TokenSet"


class Float(Number):
    def __init__(self):
        super().__init__()

    def is_valid_token(self, s: str):
        """
        only american floats, sorry commas
        """
        n = s.split(".")
        if len(n) == 0:
            return False

        if len(n) <= 2:
            valid = True
            for num in n:
                valid = valid and super().is_valid_token(num)

            return valid
        return False

    def is_valid_subtoken(self, s: str):
        return self.is_valid_token(s)

    def __str__(self):
        return "Float"


class TokenLoc():
    def __init__(self, t: Token, s: int, e: int, corpus: str = None):
        self.t = t
        self.s = s
        self.e = e
        self.corpus = corpus

    def text(self):
        return self.corpus[self.s:self.e]

    def __str__(self):
        if self.corpus is not None:
            return f"{self.t} Start index: {self.s} End index: {self.e} Text: {self.text()}"
        return f"{self.t} Start index: {self.s} End index: {self.e}"

    __repr__ = __str__


def reduce(token_stream):
    token_stack = []
    for token in token_stream:
        # try reducing to known AST elements
        token_stack.append(token)
        match token_stack[-3:]:
            case [
                    TokenLoc(t=Float()),
                    TokenLoc(t=Add()),
                    TokenLoc(t=Float()),
            ]:
                left, op, right = token_stack[-3:]
                token_stack = token_stack[:-3]
                token_stack.append({
                    "token": "Binop",
                    "text": left.text() + op.text() + right.text()
                })
            case [
                    TokenLoc(t=Float()),
                    TokenLoc(t=Sub()),
                    TokenLoc(t=Float()),
            ]:
                left, _, right = token_stack[-3:]
                token_stack = token_stack[:-3]
                token_stack.append({
                    "token": "Binop",
                    "text": left.text() + op.text() + right.text()
                })
            case [
                    {"token": "Binop"},
                    TokenLoc(t=Sub()),
                    TokenLoc(t=Float()),
            ]:
                left, _, right = token_stack[-3:]
                token_stack = token_stack[:-3]
                token_stack.append({
                    "token": "Binop",
                    "text": left['text'] + op.text() + right.text()
                })
            case [
                    {"token": "Binop"},
                    TokenLoc(t=Add()),
                    TokenLoc(t=Float()),
            ]:
                left, _, right = token_stack[-3:]
                token_stack = token_stack[:-3]
                token_stack.append({
                    "token": "Binop",
                    "text": left['text'] + op.text() + right.text()
                })
            case _:
                continue
    return token_stack


def tokenize(corpus: str, token_types: List[Token]) -> TokenLoc:
    N = len(corpus)
    s = {str(t): None for t in token_types}
    for i in range(N):
        found_token = None
        for t in token_types:
            key = str(t)
            c = corpus[i]
            start = s[key]
            if start is None and t.is_valid_subtoken(c):
                s[key] = i
            elif start is not None and not t.is_valid_subtoken(c):
                end = i
                found_token = TokenLoc(
                    t, start, end, corpus=corpus
                )
                s[key] = None
        # only return if we don't have other tokens that this **COULD** be
        # print(found_token)
        for ttype, start in s.items():
            if start is not None and start < i:
                break
        else:
            if found_token is not None:
                yield found_token
    for t in token_types:
        key = str(t)
        start = s[key]
        end = len(corpus)
        if start is not None:
            yield TokenLoc(
                t, start, end, corpus=corpus
            )
            break


if __name__ == "__main__":
    n = Number()
    f = Float()
    corpus = "12342+1341.0-12347298.29+2134671238.0"
    print(len(corpus))
    token_types = [Float(), Add(), Sub()]
    for token in tokenize(corpus, token_types):
        print(token)
    print("REDUCED TOKEN STREAM")
    reduced = reduce(tokenize(corpus, token_types))
    for token in reduced:
        print(token)
