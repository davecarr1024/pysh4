from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Iterator, Mapping, Sequence, Sized
from . import errors, vals
from core import lexer, parser


class Expr(ABC):
    @abstractmethod
    def eval(self, scope: vals.Scope) -> vals.Val:
        ...

    @classmethod
    @abstractmethod
    def load(cls, scope: parser.Scope['Expr'], state: lexer.TokenStream) -> parser.StateAndResult['Expr']:
        ...


@dataclass(frozen=True)
class Arg:
    value: Expr

    def __str__(self) -> str:
        return str(self.value)

    def eval(self, scope: vals.Scope) -> vals.Arg:
        return vals.Arg(self.value.eval(scope))

    @staticmethod
    def load(scope: parser.Scope[Expr], state: lexer.TokenStream) -> tuple[lexer.TokenStream, 'Arg']:
        state, value = parser.Ref[Expr]('expr')(scope, state)
        return state, Arg(value)


@dataclass(frozen=True)
class Args(Iterable[Arg], Sized):
    _args: Sequence[Arg]

    def __str__(self) -> str:
        return f'({", ".join(str(arg) for arg in self._args)})'

    def __len__(self) -> int:
        return len(self._args)

    def __iter__(self) -> Iterator[Arg]:
        return iter(self._args)

    def eval(self, scope: vals.Scope) -> vals.Args:
        return vals.Args([arg.eval(scope) for arg in self._args])

    @staticmethod
    def load(scope: parser.Scope[Expr], state: lexer.TokenStream) -> tuple[lexer.TokenStream, 'Args']:
        def load_arg(arg_scope: parser.Scope[Arg], state: lexer.TokenStream) -> parser.StateAndResult[Arg]:
            state, value = parser.Ref[Expr]('expr')(scope, state)
            return state, Arg(value)

        def load_tail_arg(arg_scope: parser.Scope[Arg], state: lexer.TokenStream) -> parser.StateAndResult[Arg]:
            state = parser.consume_token(state, ',')
            return load_arg(arg_scope, state)

        def load_args(arg_scope: parser.Scope[Arg], state: lexer.TokenStream) -> parser.StateAndMultipleResult[Arg]:
            state, head = load_arg(arg_scope, state)
            state, tail = parser.ZeroOrMore[Arg](
                load_tail_arg)(arg_scope, state)
            return state, [head] + list(tail)

        state = parser.consume_token(state, '(')
        args: Sequence[Arg] = []
        try:
            state, args = load_args(parser.Scope[Arg]({}), state)
        except errors.Error:
            pass
        state = parser.consume_token(state, ')')
        return state, Args(args)


@dataclass(frozen=True)
class Literal(Expr):
    value: vals.Val

    def __str__(self) -> str:
        return str(self.value)

    def eval(self, scope: vals.Scope) -> vals.Val:
        return self.value

    @classmethod
    def load(cls, scope: parser.Scope['Expr'], state: lexer.TokenStream) -> parser.StateAndResult['Expr']:
        from . import builtins_
        token = state.head
        funcs: Mapping[str, Callable[[str], Expr]] = {
            'int': lambda value: Literal(builtins_.int_(int(value))),
            'float': lambda value: Literal(builtins_.float_(float(value))),
            'str': lambda value: Literal(builtins_.str_(value[1:-1])),
        }
        if token.rule_name not in funcs:
            raise errors.Error(msg=f'unknown literal type {token.rule_name}')
        return state.tail, funcs[token.rule_name](token.value)


@dataclass(frozen=True)
class Ref(Expr):
    class Part(ABC):
        @abstractmethod
        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            ...

        @classmethod
        @abstractmethod
        def load(cls, scope: parser.Scope[Expr], state: lexer.TokenStream) -> parser.StateAndResult['Ref.Part']:
            ...

    @dataclass(frozen=True)
    class Member(Part):
        name: str

        def __str__(self) -> str:
            return f'.{self.name}'

        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            if not self.name in object_:
                raise errors.Error(
                    msg=f'unknown member {self.name} in object {object_}')
            return object_[self.name]

        @classmethod
        def load(cls, scope: parser.Scope[Expr], state: lexer.TokenStream) -> parser.StateAndResult['Ref.Part']:
            state = parser.consume_token(state, '.')
            state, value = parser.get_token_value(state, 'id')
            return state, Ref.Member(value)

    @dataclass(frozen=True)
    class Call(Part):
        args: Args

        def __str__(self) -> str:
            return str(self.args)

        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            return object_(scope, self.args.eval(scope))

    root: Expr
    parts: Sequence[Part]

    def __str__(self) -> str:
        return str(self.root) + ''.join(str(part) for part in self.parts)

    def eval(self, scope: vals.Scope) -> vals.Val:
        object_ = self.root.eval(scope)
        for part in self.parts:
            object_ = part.eval(scope, object_)
        return object_


@dataclass(frozen=True)
class BinaryOperation(Expr):

    class Operator(Enum):
        ADD = '+'
        SUB = '-'
        MUL = '*'
        DIV = '/'
        AND = 'and'
        OR = 'or'

    operator: Operator
    lhs: Expr
    rhs: Expr

    def __str__(self) -> str:
        return f'{self.lhs} {self.operator.value} {self.rhs}'

    @staticmethod
    def _func_for_operator(operator: 'BinaryOperation.Operator') -> str:
        return f'__{operator.name.lower()}__'

    def eval(self, scope: vals.Scope) -> vals.Val:
        lhs = self.lhs.eval(scope)
        rhs = self.rhs.eval(scope)
        func = lhs[self._func_for_operator(self.operator)]
        return func(scope, vals.Args([vals.Arg(rhs)]))
