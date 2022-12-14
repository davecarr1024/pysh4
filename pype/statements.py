from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional, Sequence, Sized, final
from . import errors, builtins_, exprs, vals
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
        from . import func
        return parser.Or[Statement]([
            Return.load,
            Class.load,
            Namespace.load,
            ExprStatement.load,
            func.Decl.load,
            If.load,
            While.load,
            For.load,
        ])(scope, state)

    @staticmethod
    def default_scope() -> parser.Scope['Statement']:
        return parser.Scope[Statement]({
            'statement': Statement.load,
        })

    @staticmethod
    def load_state(state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        return Statement.load(Statement.default_scope(), state)


@dataclass(frozen=True, repr=False)
class Block(Iterable[Statement], Sized):
    _statements: Sequence[Statement]

    def __repr__(self) -> str:
        return f'{{{" ".join(repr(statement) for statement in self._statements)}}}'

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

    @staticmethod
    def loader(scope: parser.Scope[Statement]) -> parser.Rule['Block']:
        def inner(_: parser.Scope[Block], state: lexer.TokenStream) -> parser.StateAndResult[Block]:
            state = parser.consume_token(state, '{')
            state, values = parser.ZeroOrMore[Statement](
                Statement.load)(scope, state)
            state = parser.consume_token(state, '}')
            return state, Block(values)
        return inner

    @staticmethod
    def load(state: lexer.TokenStream) -> parser.StateAndResult['Block']:
        return Block.loader(Statement.default_scope())(parser.Scope[Block]({}), state)


@dataclass(frozen=True)
class ExprStatement(Statement):
    value: exprs.Expr

    def eval(self, scope: vals.Scope) -> Result:
        self.value.eval(scope)
        return Result()

    @classmethod
    def load(cls, scope: parser.Scope['Statement'], state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        state, value = exprs.Expr.load_state(state)
        state = parser.consume_token(state, ';')
        return state, ExprStatement(value)


def assignment(ref: exprs.Ref, value: exprs.Expr) -> ExprStatement:
    return ExprStatement(exprs.Assignment(ref, value))


@dataclass(frozen=True)
class Return(Statement):
    value: Optional[exprs.Expr] = None

    def eval(self, scope: vals.Scope) -> Result:
        if self.value is not None:
            return Result(return_=Result.Return(self.value.eval(scope)))
        return Result(return_=Result.Return())

    @classmethod
    def load(cls, scope: parser.Scope['Statement'], state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        state = parser.consume_token(state, 'return')
        state, value = parser.ZeroOrOne[exprs.Expr](
            exprs.Expr.load)(exprs.Expr.default_scope(), state)
        state = parser.consume_token(state, ';')
        return state, Return(value=value)


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

    @classmethod
    def load(cls, scope: parser.Scope[Statement], state: lexer.TokenStream) -> parser.StateAndResult[Statement]:
        state = parser.consume_token(state, 'class')
        state, name = parser.get_token_value(state, 'id')
        state, body = Block.load(state)
        return state, Class(name, body)


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

    @classmethod
    def load(cls, scope: parser.Scope[Statement], state: lexer.TokenStream) -> parser.StateAndResult[Statement]:
        state = parser.consume_token(state, 'namespace')
        name: Optional[str] = None
        try:
            state, name = parser.get_token_value(state, 'id')
        except errors.Error:
            pass
        state, body = Block.load(state)
        return state, Namespace(body, _name=name)


@dataclass(frozen=True)
class If(Statement):
    cond: exprs.Expr
    consequent: Block
    alternative: Optional[Block] = None

    def eval(self, scope: vals.Scope) -> Result:
        if builtins_.Bool.from_val(scope, self.cond.eval(scope)):
            return self.consequent.eval(scope)
        elif self.alternative is not None:
            return self.alternative.eval(scope)
        else:
            return Result()

    @classmethod
    def load(cls, scope: parser.Scope['Statement'], state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        state = parser.consume_token(state, 'if')
        state = parser.consume_token(state, '(')
        state, cond = exprs.Expr.load_state(state)
        state = parser.consume_token(state, ')')
        state, consequent = Block.load(state)

        def load_alternative(_: parser.Scope[Block], state: lexer.TokenStream) -> parser.StateAndResult[Block]:
            state = parser.consume_token(state, 'else')
            state, alternative = Block.load(state)
            return state, alternative

        state, alternative = parser.ZeroOrOne[Block](load_alternative)(
            parser.Scope[Block]({}), state)
        return state, If(cond, consequent, alternative)


@dataclass(frozen=True, repr=False)
class While(Statement):
    cond: exprs.Expr
    body: Block

    def __repr__(self) -> str:
        return f'while ({self.cond}) {self.body}'

    def eval(self, scope: vals.Scope) -> Result:
        while builtins_.Bool.from_val(scope, self.cond.eval(scope)):
            result = self.body.eval(scope)
            if result.return_ is not None:
                return result
        return Result()

    @classmethod
    def load(cls, scope: parser.Scope['Statement'], state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        state = parser.consume_token(state, 'while')
        state = parser.consume_token(state, '(')
        state, cond = exprs.Expr.load_state(state)
        state = parser.consume_token(state, ')')
        state, body = Block.load(state)
        return state, While(cond, body)


@dataclass(frozen=True, repr=False)
class For(Statement):
    init: exprs.Expr
    cond: exprs.Expr
    step: exprs.Expr
    body: Block

    def __repr__(self) -> str:
        return f'for ({self.init}; {self.cond}; {self.step}) {self.body}'

    def eval(self, scope: vals.Scope) -> Result:
        self.init.eval(scope)
        while builtins_.Bool.from_val(scope, self.cond.eval(scope)):
            result = self.body.eval(scope)
            if result.return_ is not None:
                return result
            self.step.eval(scope)
        return Result()

    @classmethod
    def load(cls, scope: parser.Scope['Statement'], state: lexer.TokenStream) -> parser.StateAndResult['Statement']:
        state = parser.consume_token(state, 'for')
        state = parser.consume_token(state, '(')
        state, init = exprs.Expr.load_state(state)
        state = parser.consume_token(state, ';')
        state, cond = exprs.Expr.load_state(state)
        state = parser.consume_token(state, ';')
        state, step = exprs.Expr.load_state(state)
        state = parser.consume_token(state, ')')
        state, body = Block.load(state)
        return state, For(init, cond, step, body)
