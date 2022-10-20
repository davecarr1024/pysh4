from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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
        return parser.Or[Expr]([
            BinaryOperation.load,
            Ref.load,
        ])(scope, state)

    @staticmethod
    def default_scope() -> parser.Scope['Expr']:
        return parser.Scope[Expr]({
            'expr': Expr.load,
            'operand': Ref.load,
        })

    @staticmethod
    def load_state(state: lexer.TokenStream) -> parser.StateAndResult['Expr']:
        return Expr.load(Expr.default_scope(), state)


@dataclass(frozen=True, repr=False)
class Arg:
    value: Expr

    def __repr__(self) -> str:
        return repr(self.value)

    def eval(self, scope: vals.Scope) -> vals.Arg:
        return vals.Arg(self.value.eval(scope))

    @staticmethod
    def loader(scope: parser.Scope[Expr]) -> parser.Rule['Arg']:
        def inner(_: parser.Scope[Arg], state: lexer.TokenStream) -> parser.StateAndResult[Arg]:
            state, value = parser.Ref[Expr]('expr')(scope, state)
            return state, Arg(value)
        return inner


@dataclass(frozen=True, repr=False)
class Args(Iterable[Arg], Sized):
    _args: Sequence[Arg]

    def __repr__(self) -> str:
        return f'({", ".join(repr(arg) for arg in self._args)})'

    def __len__(self) -> int:
        return len(self._args)

    def __iter__(self) -> Iterator[Arg]:
        return iter(self._args)

    def eval(self, scope: vals.Scope) -> vals.Args:
        return vals.Args([arg.eval(scope) for arg in self._args])

    @staticmethod
    def load(scope: parser.Scope[Expr], state: lexer.TokenStream) -> tuple[lexer.TokenStream, 'Args']:
        load_arg = Arg.loader(scope)

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


@dataclass(frozen=True, repr=False)
class Ref(Expr):
    class Tail(ABC):
        @abstractmethod
        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            ...

        @abstractmethod
        def assign(self, scope: vals.Scope, object_: vals.Val, value: vals.Val) -> None:
            ...

        @classmethod
        @abstractmethod
        def loader(cls, scope: parser.Scope[Expr]) -> parser.Rule['Ref.Tail']:
            return parser.Or[Ref.Tail]([
                Ref.Member.loader(scope),
                Ref.Call.loader(scope),
            ])

        @staticmethod
        def load(scope: parser.Scope[Expr], state: lexer.TokenStream) -> parser.StateAndMultipleResult['Ref.Tail']:
            return parser.ZeroOrMore[Ref.Tail](Ref.Tail.loader(scope))(parser.Scope[Ref.Tail]({}), state)

    @dataclass(frozen=True)
    class Member(Tail):
        name: str

        def __repr__(self) -> str:
            return f'.{self.name}'

        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            if not self.name in object_:
                raise errors.Error(
                    msg=f'unknown member {self.name} in object {object_}')
            return object_[self.name]

        def assign(self, scope: vals.Scope, object_: vals.Val, value: vals.Val) -> None:
            object_[self.name] = value

        @classmethod
        def loader(cls, scope: parser.Scope[Expr]) -> parser.Rule['Ref.Tail']:
            def inner(_: parser.Scope[Ref.Tail], state: lexer.TokenStream) -> parser.StateAndResult[Ref.Tail]:
                state = parser.consume_token(state, '.')
                state, value = parser.get_token_value(state, 'id')
                return state, Ref.Member(value)
            return inner

    @dataclass(frozen=True)
    class Call(Tail):
        args: Args

        def __repr__(self) -> str:
            return repr(self.args)

        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            return object_(scope, self.args.eval(scope))

        def assign(self, scope: vals.Scope, object_: vals.Val, value: vals.Val) -> None:
            raise errors.Error(msg=f'call {self} is not assignable')

        @classmethod
        def loader(cls, scope: parser.Scope[Expr]) -> parser.Rule['Ref.Tail']:
            def inner(_: parser.Scope[Ref.Tail], state: lexer.TokenStream) -> parser.StateAndResult[Ref.Tail]:
                state, args = Args.load(scope, state)
                return state, Ref.Call(args)
            return inner

    class Head(ABC):
        @abstractmethod
        def eval(self, scope: vals.Scope) -> vals.Val:
            ...

        @abstractmethod
        def assign(self, scope: vals.Scope, value: vals.Val) -> None:
            ...

        @classmethod
        @abstractmethod
        def load(cls, scope: parser.Scope['Ref.Head'], state: lexer.TokenStream) -> parser.StateAndResult['Ref.Head']:
            return parser.Or[Ref.Head]([
                Ref.Name.load,
                Ref.Literal.load,
            ])(scope, state)

    @dataclass(frozen=True)
    class Name(Head):
        name: str

        def eval(self, scope: vals.Scope) -> vals.Val:
            if self.name not in scope:
                raise errors.Error(msg=f'unknown name {self.name}')
            return scope[self.name]

        def assign(self, scope: vals.Scope, value: vals.Val) -> None:
            scope[self.name] = value

        @classmethod
        def load(cls, scope: parser.Scope['Ref.Head'], state: lexer.TokenStream) -> parser.StateAndResult['Ref.Head']:
            state, value = parser.get_token_value(state, 'id')
            return state, Ref.Name(value)

    @dataclass(frozen=True)
    class Literal(Head):
        value: vals.Val

        def eval(self, scope: vals.Scope) -> vals.Val:
            return self.value

        def assign(self, scope: vals.Scope, value: vals.Val) -> None:
            raise errors.Error(msg=f'literal {self} is not assignable')

        @staticmethod
        def load_value(state: lexer.TokenStream) -> parser.StateAndResult[vals.Val]:
            from . import builtins_
            token = state.head
            funcs: Mapping[str, Callable[[str], vals.Val]] = {
                'int': lambda value: builtins_.int_(int(value)),
                'float': lambda value: builtins_.float_(float(value)),
                'str': lambda value: builtins_.str_(value[1:-1]),
            }
            if token.rule_name not in funcs:
                raise errors.Error(
                    msg=f'unknown literal type {token.rule_name}')
            return state.tail, funcs[token.rule_name](token.value)

        @classmethod
        def load(cls,  scope: parser.Scope['Ref.Head'], state: lexer.TokenStream) -> parser.StateAndResult['Ref.Head']:
            state, value = cls.load_value(state)
            return state, Ref.Literal(value)

    head: Head
    tail: Sequence[Tail] = field(default_factory=list[Tail])

    def __repr__(self) -> str:
        return repr(self.head) + ''.join(repr(part) for part in self.tail)

    def eval(self, scope: vals.Scope) -> vals.Val:
        object_ = self.head.eval(scope)
        for part in self.tail:
            object_ = part.eval(scope, object_)
        return object_

    def assign(self, scope: vals.Scope, value: vals.Val) -> None:
        if len(self.tail) == 0:
            self.head.assign(scope, value)
        else:
            object_ = self.head.eval(scope)
            for part in self.tail[:-1]:
                object_ = part.eval(scope, object_)
            self.tail[-1].assign(scope, object_, value)

    @classmethod
    def load(cls, scope: parser.Scope['Expr'], state: lexer.TokenStream) -> parser.StateAndResult['Ref']:
        state, head = Ref.Head.load(parser.Scope[Ref.Head]({}), state)
        state, tail = Ref.Tail.load(scope, state)
        return state, Ref(head, tail)


def literal(value: vals.Val) -> Ref:
    return Ref(Ref.Literal(value))


def ref(name: str) -> Ref:
    return Ref(Ref.Name(name))


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

    def __repr__(self) -> str:
        return f'{self.lhs} {self.operator.value} {self.rhs}'

    @staticmethod
    def _func_for_operator(operator: 'BinaryOperation.Operator') -> str:
        return f'__{operator.name.lower()}__'

    def eval(self, scope: vals.Scope) -> vals.Val:
        lhs = self.lhs.eval(scope)
        rhs = self.rhs.eval(scope)
        return lhs[self._func_for_operator(self.operator)](scope, vals.Args([vals.Arg(rhs)]))

    @classmethod
    def load(cls, scope: parser.Scope[Expr], state: lexer.TokenStream) -> parser.StateAndResult[Expr]:
        state, lhs = parser.Ref[Expr]('operand')(scope, state)
        operator_value = state.head.value
        if not any(operator.value == operator_value for operator in BinaryOperation.Operator):
            raise parser.StateError(
                msg=f'unknown operator {operator_value}', state=state)
        state = state.tail
        operator = BinaryOperation.Operator(operator_value)
        state, rhs = parser.Ref[Expr]('operand')(scope, state)
        return state, BinaryOperation(operator, lhs, rhs)
