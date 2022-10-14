from dataclasses import dataclass
from typing import Tuple, TypeVar
from . import errors, lexer, processor, stream

_Result = TypeVar('_Result')

StateError = processor.StateError[lexer.TokenStream]
RuleError = processor.RuleError[lexer.TokenStream, _Result]
Rule = processor.Rule[lexer.TokenStream, _Result]
Scope = processor.Scope[lexer.TokenStream, _Result]
StateAndResult = processor.StateAndResult[lexer.TokenStream, _Result]
Ref = processor.Ref[lexer.TokenStream, _Result]
Or = processor.Or[lexer.TokenStream, _Result]
And = processor.And[lexer.TokenStream, _Result]
ZeroOrMore = processor.ZeroOrMore[lexer.TokenStream, _Result]
OneOrMore = processor.OneOrMore[lexer.TokenStream, _Result]
ZeroOrOne = processor.ZeroOrOne[lexer.TokenStream, _Result]
UntilEmpty = stream.UntilEmpty[lexer.TokenStream, _Result]
UnaryRule = processor.UnaryRule[lexer.TokenStream, _Result]
NaryRule = processor.NaryRule[lexer.TokenStream, _Result]
ResultCombiner = processor.ResultCombiner[_Result]


@dataclass(frozen=True, init=False)
class Parser(processor.Processor[lexer.TokenStream, _Result]):
    def __init__(self, **rules: Rule[_Result]):
        super().__init__(
            rules,
            list(rules.keys())[0]
        )


def get_token_value(state: lexer.TokenStream, rule_name: str) -> Tuple[lexer.TokenStream, str]:
    if state.empty:
        raise errors.Error(msg='empty stream')
    if state.head.rule_name != rule_name:
        raise errors.Error(
            msg=f'expected token rule_name {rule_name} got {state.head.rule_name}')
    return state.tail, state.head.value


def consume_token(state: lexer.TokenStream, rule_name: str) -> lexer.TokenStream:
    if state.empty:
        raise errors.Error(msg='empty stream')
    if state.head.rule_name != rule_name:
        raise errors.Error(
            msg=f'expected token rule_name {rule_name} got {state.head.rule_name}')
    return state.tail
