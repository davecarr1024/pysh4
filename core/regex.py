from dataclasses import dataclass
from typing import Sequence, TypeVar

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


Rule = processor.Rule[CharStream[_Char], Token]
Scope = processor.Scope[CharStream[_Char], Token]
StateAndResult = processor.StateAndResult[CharStream[_Char], Token]


def or_(*rules: Rule[_Char]) -> Rule[_Char]:
    return processor.or_(*rules)


def and_(*rules: Rule[_Char]) -> Rule[_Char]:
    return processor.and_(rules, Token.concat)


def zero_or_more(rule: Rule[_Char]) -> Rule[_Char]:
    return processor.zero_or_more(rule, Token.concat)


def one_or_more(rule: Rule[_Char]) -> Rule[_Char]:
    return processor.one_or_more(rule, Token.concat)


def zero_or_one(rule: Rule[_Char]) -> Rule[_Char]:
    return processor.zero_or_one(rule, Token.concat)


def until_empty(rule: Rule[_Char]) -> Rule[_Char]:
    return stream.until_empty(rule, Token.concat)


def literal(value: str) -> Rule[_Char]:
    if len(value) != 1:
        raise errors.Error(msg=f'invalid value {value}')

    def closure(scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        if state.head.value != value:
            raise errors.Error(
                msg=f'expected {repr(value)} but got {repr(state.head)}')
        return state.tail, Token(state.head.value)
    return closure
