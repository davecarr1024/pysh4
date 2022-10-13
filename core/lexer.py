from dataclasses import dataclass
from typing import MutableSequence, Sequence
from . import processor, stream, regex


@dataclass(frozen=True)
class Position:
    line: int
    column: int


@dataclass(frozen=True, repr=False)
class Char(regex.Char):
    position: Position


class CharStream(regex.CharStream[Char]):
    ...


def load_char_stream(input: str) -> CharStream:
    line: int = 0
    column: int = 0
    chars: MutableSequence[Char] = []
    for char in input:
        chars.append(Char(char, Position(line, column)))
        if char == '\n':
            line += 1
            column = 0
        else:
            column += 1
    return CharStream(chars)


@dataclass(frozen=True)
class Token(regex.Token):
    rule_name: str
    position: Position


class TokenStream(stream.Stream[Token]):
    ...


Rule = processor.Rule[CharStream, TokenStream]
Scope = processor.Scope[CharStream, TokenStream]
StateAndResult = processor.StateAndResult[CharStream, TokenStream]
_Ref = processor.Ref[CharStream, TokenStream]
_Or = processor.Or[CharStream, TokenStream]


class _ResultCombiner(processor.ResultCombiner[TokenStream]):
    def combine_results(self, results: Sequence[TokenStream]) -> TokenStream:
        return sum(results, TokenStream())


class _UntilEmpty(stream.UntilEmpty[CharStream, TokenStream], _ResultCombiner):
    ...


_RULE_PREFIX = '_lexer'
_ROOT_RULE_NAME = f'{_RULE_PREFIX}_root'
_REGEX_RULE_NAME = f'{_RULE_PREFIX}_regexes'


@dataclass(frozen=True, repr=False)
class _Regex:
    rule_name: str
    rule: regex.Rule[Char]

    def __call__(self, scope: Scope, state: CharStream) -> StateAndResult:
        position = state.head.position
        state, token = self.rule(scope, state)
        return state, TokenStream([Token(token.value, self.rule_name, position)])


@dataclass(frozen=True, init=False, repr=False)
class Lexer(processor.Processor[CharStream, TokenStream]):
    def __init__(self, **rules: regex.Rule[Char]):
        super().__init__(
            {
                _ROOT_RULE_NAME: _UntilEmpty(_Ref(_REGEX_RULE_NAME)),
                _REGEX_RULE_NAME: _Or([
                    _Regex(rule_name, rule) for rule_name, rule in rules.items()
                ])
            },
            _ROOT_RULE_NAME,
        )
