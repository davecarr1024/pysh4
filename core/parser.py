from dataclasses import dataclass
from typing import Tuple, TypeVar, overload
from . import lexer, processor, stream

_Result = TypeVar('_Result')

StateError = processor.StateError[lexer.TokenStream]
RuleError = processor.RuleError[lexer.TokenStream, _Result]
Rule = processor.Rule[lexer.TokenStream, _Result]
MultipleResultRule = processor.MultipleResultRule[lexer.TokenStream, _Result]
Scope = processor.Scope[lexer.TokenStream, _Result]
StateAndResult = processor.StateAndResult[lexer.TokenStream, _Result]
StateAndMultipleResult = processor.StateAndMultipleResult[lexer.TokenStream, _Result]
Ref = processor.Ref[lexer.TokenStream, _Result]
Or = processor.Or[lexer.TokenStream, _Result]
And = processor.And[lexer.TokenStream, _Result]
ZeroOrMore = processor.ZeroOrMore[lexer.TokenStream, _Result]
OneOrMore = processor.OneOrMore[lexer.TokenStream, _Result]
ZeroOrOne = processor.ZeroOrOne[lexer.TokenStream, _Result]
UntilEmpty = stream.UntilEmpty[lexer.TokenStream, _Result]
UnaryRule = processor.UnaryRule[lexer.TokenStream, _Result]
NaryRule = processor.NaryRule[lexer.TokenStream, _Result]
ResultCombiner = processor.ResultCombiner[lexer.TokenStream, _Result]


@dataclass(frozen=True)
class Parser(processor.Processor[lexer.TokenStream, _Result]):
    lexer_: lexer.Lexer

    @overload
    def __call__(self, scope: Scope[_Result], state: lexer.TokenStream) -> StateAndResult[_Result]:
        ...

    @overload
    def __call__(self, scope: Scope[_Result], state: str) -> StateAndResult[_Result]:
        ...

    def __call__(self, scope: Scope[_Result], state: lexer.TokenStream | str) -> StateAndResult[_Result]:
        if isinstance(state, str):
            _, state = self.lexer_(lexer.Scope({}), state)
        return super().__call__(scope, state)


def get_token_value(state: lexer.TokenStream, rule_name: str) -> Tuple[lexer.TokenStream, str]:
    if state.empty:
        raise StateError(msg='empty stream', state=state)
    if state.head.rule_name != rule_name:
        raise StateError(state=state,
                         msg=f'expected token {rule_name} got {state.head.rule_name}')
    return state.tail, state.head.value


def consume_token(state: lexer.TokenStream, rule_name: str) -> lexer.TokenStream:
    if state.empty:
        raise StateError(state=state, msg='empty stream')
    if state.head.rule_name != rule_name:
        raise StateError(state=state,
                         msg=f'expected token {rule_name} got {state.head.rule_name}')
    return state.tail
