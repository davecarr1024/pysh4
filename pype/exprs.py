from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Iterator, Sequence, Sized
from . import errors, vals
from core import lexer, parser


class Expr(ABC):
    @abstractmethod
    def eval(self, scope: vals.Scope) -> vals.Val:
        ...

    @abstractmethod
    @classmethod
    def load(cls, scope: parser.Scope['Expr'], state: lexer.TokenStream) -> parser.StateAndResult['Expr']:
        ...


@dataclass(frozen=True)
class Arg:
    value: Expr

    def __str__(self) -> str:
        return str(self.value)

    def eval(self, scope: vals.Scope) -> vals.Arg:
        return vals.Arg(self.value.eval(scope))


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


@dataclass(frozen=True)
class Ref(Expr):
    name: str

    def __str__(self) -> str:
        return self.name

    def eval(self, scope: vals.Scope) -> vals.Val:
        if self.name not in scope:
            raise errors.Error(f'unknown ref {self.name}')
        return scope[self.name]


@dataclass(frozen=True)
class Literal(Expr):
    value: vals.Val

    def __str__(self) -> str:
        return str(self.value)

    def eval(self, scope: vals.Scope) -> vals.Val:
        return self.value


@dataclass(frozen=True)
class Path(Expr):
    class Part(ABC):
        @abstractmethod
        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            ...

    @dataclass(frozen=True)
    class Member(Part):
        '''gets a member of an object'''

        name: str

        def __str__(self) -> str:
            return f'.{self.name}'

        def eval(self, scope: vals.Scope, object_: vals.Val) -> vals.Val:
            if not self.name in object_:
                raise errors.Error(
                    f'unknown member {self.name} in object {object_}')
            return object_[self.name]

    @dataclass(frozen=True)
    class Call(Part):
        '''calls an object with args'''

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
