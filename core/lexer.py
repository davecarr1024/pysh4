from dataclasses import dataclass
from typing import MutableSequence, OrderedDict, Sequence
from . import processor, stream, regex


@dataclass(frozen=True)
class Position:
    line: int
    column: int


@dataclass(frozen=True)
class Char(regex.Char):
    position: Position


CharStream = stream.Stream[Char]


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


def _result_combiner(results: Sequence[TokenStream]) -> TokenStream:
    return sum(results, TokenStream())


def lexer(rules: OrderedDict[str, regex.Rule[Char]]) -> Rule:
    def _regex_rule(rule_name: str, regex_: regex.Rule[Char]) -> Rule:
        def closure(scope: Scope, state: CharStream) -> StateAndResult:
            position = state.head.position
            state, token = regex_(regex.Scope[Char](), state)
            return state, TokenStream([Token(value=token.value, rule_name=rule_name, position=position)])
        return closure

    def _regex_rules(rules: OrderedDict[str, regex.Rule[Char]]) -> Rule:
        return processor.or_(*[_regex_rule(name, rule) for name, rule in rules.items()])

    return stream.until_empty(_regex_rules(rules), _result_combiner)
