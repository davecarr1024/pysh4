from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

from . import errors, processor, stream


@dataclass(frozen=True)
class Char:
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid value {self.value}')

    def __repr__(self) -> str:
        return repr(self.value)


_Char = TypeVar('_Char', bound=Char, covariant=True)

CharStream = stream.Stream[_Char]


@dataclass(frozen=True)
class Token:
    value: str

    def __add__(self, rhs: 'Token') -> 'Token':
        return Token(self.value + rhs.value)

    @staticmethod
    def concat(tokens: Sequence['Token']) -> 'Token':
        return sum(tokens, Token(''))


RuleError = processor.RuleError[CharStream[_Char], Token]
Rule = processor.Rule[CharStream[_Char], Token]
Scope = processor.Scope[CharStream[_Char], Token]
StateAndResult = processor.StateAndResult[CharStream[_Char], Token]
Ref = processor.Ref[CharStream[_Char], Token]
Or = processor.Or[CharStream[_Char], Token]


class _ResultCombiner(processor.ResultCombiner[Token]):
    def combine_results(self, results: Sequence[Token]) -> Token:
        return Token.concat(results)


class And(processor.And[CharStream[_Char], Token], _ResultCombiner):
    ...


class ZeroOrMore(processor.ZeroOrMore[CharStream[_Char], Token], _ResultCombiner):
    ...


class OneOrMore(processor.OneOrMore[CharStream[_Char], Token], _ResultCombiner):
    ...


class ZeroOrOne(processor.ZeroOrOne[CharStream[_Char], Token], _ResultCombiner):
    ...


class UntilEmpty(stream.UntilEmpty[CharStream[_Char], Token], _ResultCombiner):
    ...


@dataclass(frozen=True, repr=False)
class Literal(Generic[_Char]):
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid literal value {self.value}')

    def __repr__(self) -> str:
        return repr(self.value)

    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        if state.empty:
            raise RuleError[_Char](rule=self, state=state, msg='empty stream')
        if state.head.value != self.value:
            raise RuleError[_Char](
                rule=self, state=state, msg=f'expected {repr(self.value)} but got {state.head}')
        return state.tail, Token(state.head.value)


@dataclass(frozen=True, repr=False)
class Not(processor.UnaryRule[CharStream[_Char], Token]):
    def __repr__(self) -> str:
        return f'^{self.rule}'

    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        try:
            self.rule(scope, state)
        except errors.Error:
            return state.tail, Token(state.head.value)
        raise RuleError[_Char](rule=self, state=state,
                               msg=f'successfully applied not rule')


@dataclass(frozen=True, repr=False)
class Class(Generic[_Char]):
    values: Sequence[str]

    def __post_init__(self):
        for value in self.values:
            if len(value) != 1:
                raise errors.Error(msg=f'invalid literal value {value}')

    def __repr__(self) -> str:
        return repr(self.values)

    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        if state.empty:
            raise RuleError[_Char](rule=self, state=state, msg='empty stream')
        if state.head.value not in self.values:
            raise RuleError[_Char](
                rule=self, state=state, msg=f'expected {repr(self.values)} but got {state.head}')
        return state.tail, Token(state.head.value)
