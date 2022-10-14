from dataclasses import dataclass
from typing import MutableSequence, Sequence, overload
from . import processor, stream, regex


@dataclass(frozen=True)
class Position:
    line: int
    column: int


@dataclass(frozen=True, repr=False)
class Char(regex.Char):
    position: Position


CharStream = regex.CharStream[Char]


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


TokenStream = stream.Stream[Token]


Rule = processor.Rule[CharStream, TokenStream]
Scope = processor.Scope[CharStream, TokenStream]
StateAndResult = processor.StateAndResult[CharStream, TokenStream]
_Ref = processor.Ref[CharStream, TokenStream]
_Or = processor.Or[CharStream, TokenStream]

ReOr = regex.Or[Char]
ReAnd = regex.And[Char]
ReZeroOrMore = regex.ZeroOrMore[Char]
ReOneOrMore = regex.OneOrMore[Char]
ReZeroOrOne = regex.ZeroOrOne[Char]
ReUntilEmpty = regex.UntilEmpty[Char]
ReLiteral = regex.Literal[Char]
ReNot = regex.Not[Char]
ReClass = regex.Class[Char]
ReRange = regex.Range[Char]


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
    name: str
    rule: regex.Rule[Char]

    def __call__(self, scope: Scope, state: CharStream) -> StateAndResult:
        position = state.head.position
        state, token = self.rule(regex.Scope[Char]({}), state)
        return state, TokenStream([Token(token.value, self.name, position)])


@dataclass(frozen=True, init=False, repr=False)
class Lexer(processor.Processor[CharStream, TokenStream]):
    def __init__(self, **rules: regex.Rule[Char]):
        super().__init__(
            {
                _ROOT_RULE_NAME: _UntilEmpty(_Ref(_REGEX_RULE_NAME)),
                _REGEX_RULE_NAME: _Or([
                    _Regex(name, rule) for name, rule in rules.items()
                ])
            },
            _ROOT_RULE_NAME,
        )

    @overload
    def __call__(self, scope: Scope, state: CharStream) -> StateAndResult:
        ...

    @overload
    def __call__(self, scope: Scope, state: str) -> StateAndResult:
        ...

    def __call__(self, scope: Scope, state: CharStream | str) -> StateAndResult:
        if isinstance(state, str):
            state = load_char_stream(state)
        return super().__call__(scope, state)
