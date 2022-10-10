from dataclasses import dataclass
import string
from typing import Collection, Sequence, TypeVar
from . import errors, stream_processor


@dataclass(frozen=True)
class Char:
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid char value {repr(self.value)}')


_Char = TypeVar('_Char', bound=Char)

CharStream = stream_processor.Stream[_Char]
StateAndResult = stream_processor.StateAndResult[_Char, str]
Rule = stream_processor.Rule[_Char, str]
Scope = stream_processor.Scope[_Char, str]
Ref = stream_processor.Ref[_Char, str]
Or = stream_processor.Or[_Char, str]
_HeadRule = stream_processor.HeadRule[_Char, str]


@dataclass(frozen=True)
class Regex(stream_processor.Processor[_Char, str]):
    ...


class ResultCombiner(stream_processor.ResultCombiner[str]):
    def combine_results(self, results: Sequence[str]) -> str:
        return ''.join(results)


class And(stream_processor.And[_Char, str], ResultCombiner):
    ...


class ZeroOrMore(stream_processor.ZeroOrMore[_Char, str], ResultCombiner):
    ...


class OneOrMore(stream_processor.OneOrMore[_Char, str], ResultCombiner):
    ...


class ZeroOrOne(stream_processor.ZeroOrOne[_Char, str], ResultCombiner):
    ...


class UntilEmpty(stream_processor.UntilEmpty[_Char, str], ResultCombiner):
    ...


@dataclass(frozen=True, repr=False)
class Literal(_HeadRule[_Char]):
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid literal value {repr(self.value)}')

    def __repr__(self) -> str:
        return repr(self.value)

    def result(self, head: _Char) -> str:
        if self.value != head.value:
            raise errors.Error(msg=f'head {head} != literal {self}')
        return head.value


@dataclass(frozen=True, repr=False)
class Class(_HeadRule[_Char]):
    values: Collection[str]

    def __post_init__(self):
        if len(self.values) == 0:
            raise errors.Error(msg='empty class')
        for value in self.values:
            if len(value) != 1:
                raise errors.Error(msg=f'invalid class value {repr(value)}')

    def __repr__(self) -> str:
        return repr(self.values)

    def result(self, head: _Char) -> str:
        if head.value not in self.values:
            raise errors.Error(msg=f'head {head} not in class {self}')
        return head.value

    @staticmethod
    def whitespace() -> 'Class[_Char]':
        return Class[_Char](string.whitespace)


@dataclass(frozen=True)
class Range(_HeadRule[_Char]):
    min: str
    max: str

    def __post_init__(self):
        if len(self.min) != 1:
            raise errors.Error(msg=f'invalid min {self.min}')
        if len(self.max) != 1:
            raise errors.Error(msg=f'invalid max {self.max}')
        if self.max < self.min:
            raise errors.Error(msg=f'invalid range {self}')

    def __repr__(self) -> str:
        return f'[{self.min}-{self.max}]'

    def result(self, head: _Char) -> str:
        if head.value < self.min or head.value > self.max:
            raise errors.Error(msg=f'head {head} not in range {self}')
        return head.value
