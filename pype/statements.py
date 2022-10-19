from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional, Sequence, Sized, final
from . import exprs, vals
from core import lexer, parser


@dataclass(frozen=True)
class Result:
    @dataclass(frozen=True)
    class Return:
        value: Optional[vals.Val] = None

    return_: Optional[Return] = field(kw_only=True, default=None)


class Statement(ABC):
    @abstractmethod
    def eval(self, scope: vals.Scope) -> Result:
        ...

    @classmethod
    @abstractmethod
    def load(cls, scope: parser.Scope['Statement'], state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        raise NotImplementedError()

    @staticmethod
    def default_scope() -> parser.Scope['Statement']:
        return parser.Scope[Statement]({
            'statement': Statement.load,
        })

    @staticmethod
    def load_state(state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        return Statement.load(Statement.default_scope(), state)


@dataclass(frozen=True)
class Block(Iterable[Statement], Sized):
    _statements: Sequence[Statement]

    def __len__(self) -> int:
        return len(self._statements)

    def __iter__(self) -> Iterator[Statement]:
        return iter(self._statements)

    def eval(self, scope: vals.Scope) -> Result:
        for statement in self._statements:
            result = statement.eval(scope)
            if result.return_ is not None:
                return result
        return Result()


@dataclass(frozen=True)
class Assignment(Statement):
    name: str
    value: exprs.Expr

    def eval(self, scope: vals.Scope) -> Result:
        scope[self.name] = self.value.eval(scope)
        return Result()


@dataclass(frozen=True)
class Expr(Statement):
    value: exprs.Expr

    def eval(self, scope: vals.Scope) -> Result:
        self.value.eval(scope)
        return Result()

    @classmethod
    def load(cls, scope: parser.Scope['Statement'], state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        state, value = exprs.Expr.load_state(state)
        state = parser.consume_token(state, ';')
        return state, Expr(value)


@dataclass(frozen=True)
class Return(Statement):
    value: Optional[exprs.Expr]

    def eval(self, scope: vals.Scope) -> Result:
        if self.value is not None:
            return Result(return_=Result.Return(self.value.eval(scope)))
        return Result(return_=Result.Return())


@dataclass(frozen=True)
class Decl(Statement):
    @dataclass(frozen=True)
    class Value:
        value: vals.Val
        result: Result

    @property
    @abstractmethod
    def name(self) -> Optional[str]:
        ...

    @abstractmethod
    def value(self, scope: vals.Scope) -> Value:
        ...

    @final
    def eval(self, scope: vals.Scope) -> Result:
        value = self.value(scope)
        if self.name is not None:
            scope[self.name] = value.value
        return value.result


@dataclass(frozen=True)
class Class(Decl):
    _name: str
    body: Block

    @property
    def name(self) -> str:
        return self._name

    def value(self, scope: vals.Scope) -> Decl.Value:
        members = scope.as_child()
        result = self.body.eval(members)
        return Decl.Value(vals.Class(self.name, members), result)


@dataclass(frozen=True)
class Namespace(Decl):
    _name: Optional[str] = field(kw_only=True, default=None)
    body: Block

    @property
    def name(self) -> Optional[str]:
        return self._name

    def value(self, scope: vals.Scope) -> Decl.Value:
        members = scope.as_child()
        result = self.body.eval(members)
        return Decl.Value(vals.Namespace(members, name=self.name), result)
