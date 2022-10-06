from dataclasses import dataclass
from . import errors, stream_processor


@dataclass(frozen=True)
class Char:
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid char value {repr(self.value)}')


CharStream = stream_processor.Stream[Char]
StateAndResult = stream_processor.StateAndResult[Char, str]
Rule = stream_processor.Rule[Char, str]
Scope = stream_processor.Scope[Char, str]
Ref = stream_processor.Ref[Char, str]
Or = stream_processor.Or[Char, str]
_HeadRule = stream_processor.HeadRule[Char, str]


@dataclass(frozen=True)
class LexerRule(stream_processor.Processor[Char, str]):
    ...


@dataclass(frozen=True)
class Literal(_HeadRule):
    value: Char

    def result(self, head: Char) -> str:
        if self.value != head:
            raise errors.Error(msg=f'expected {self.value} actual {head}')
        return head.value
