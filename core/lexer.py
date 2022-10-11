from dataclasses import dataclass
from typing import MutableSequence, Sequence
from . import errors, regex, stream_processor


@dataclass(frozen=True)
class Position:
    line: int
    column: int


@dataclass(frozen=True)
class Char(regex.Char):
    position: Position


CharStream = stream_processor.Stream[Char]


def load_char_stream(input_str: str) -> CharStream:
    chars: MutableSequence[Char] = []
    line = 0
    column = 0
    for char in input_str:
        chars.append(Char(char, Position(line, column)))
        if char == '\n':
            line += 1
            column = 0
        else:
            column += 1
    return CharStream(chars)


@dataclass(frozen=True, repr=False)
class Token:
    rule_name: str
    value: str
    position: Position

    def __repr__(self) -> str:
        return f'{self.rule_name}({self.value})'


TokenStream = stream_processor.Stream[Token]


class _ResultCombiner(stream_processor.ResultCombiner[TokenStream]):
    def combine_results(self, results: Sequence[TokenStream]) -> TokenStream:
        return sum(results, TokenStream([]))


Rule = stream_processor.Rule[Char, TokenStream]
RuleError = stream_processor.RuleError[Char, TokenStream]
Scope = stream_processor.Scope[Char, TokenStream]
StateAndResult = stream_processor.StateAndResult[Char, TokenStream]
_Ref = stream_processor.Ref[Char, TokenStream]
_Or = stream_processor.Or[Char, TokenStream]


class _UntilEmpty(stream_processor.UntilEmpty[Char, TokenStream], _ResultCombiner):
    ...


@dataclass(frozen=True)
class Regex(Rule):
    name: str
    regex_: regex.Rule[Char]

    def apply(self, scope: Scope, state: CharStream) -> StateAndResult:
        position = state.head.position
        try:
            regex_state_and_result = self.regex_.apply(
                regex.Scope[Char]({}), state)
        except errors.Error as error:
            raise RuleError(rule=self, state=state,
                            children=[error]) from error
        return StateAndResult(
            regex_state_and_result.state,
            TokenStream([
                Token(
                    self.name,
                    regex_state_and_result.result,
                    position,
                )
            ])
        )


_RULE_NAME_PREFIX = '_lexer'
_ROOT_RULE_NAME = f'{_RULE_NAME_PREFIX}_root'
_TOKEN_RULE_NAME = f'{_RULE_NAME_PREFIX}_token'


@dataclass(frozen=True, init=False)
class Lexer(stream_processor.Processor[Char, TokenStream]):
    def __init__(self, rules: Sequence[Regex]):
        for rule in rules:
            if rule.name.startswith(_RULE_NAME_PREFIX):
                raise errors.Error(msg=f'invalid rule_name {rule.name}')
        if len(set(rule.name for rule in rules)) != len(rules):
            raise errors.Error(msg=f'duplicate rule names')
        super().__init__(
            {
                _ROOT_RULE_NAME: _UntilEmpty(_Ref(_TOKEN_RULE_NAME)),
                _TOKEN_RULE_NAME: _Or([_Ref(rule.name) for rule in rules]),
                **{rule.name: rule for rule in rules}
            },
            _ROOT_RULE_NAME
        )
