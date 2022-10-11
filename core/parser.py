from dataclasses import dataclass
from typing import Callable, TypeVar
from . import errors, stream_processor, lexer


_Result = TypeVar('_Result')

StateError = stream_processor.StateError[lexer.Token]
RuleError = stream_processor.RuleError[lexer.Token, _Result]
RuleNameError = stream_processor.RuleNameError
StateAndResult = stream_processor.StateAndResult[lexer.Token, _Result]
Rule = stream_processor.Rule[lexer.Token, _Result]
Scope = stream_processor.Scope[lexer.Token, _Result]
UnaryRule = stream_processor.UnaryRule[lexer.Token, _Result]
NaryRule = stream_processor.NaryRule[lexer.Token, _Result]
ResultCombiner = stream_processor.ResultCombiner[_Result]
Ref = stream_processor.Ref[lexer.Token, _Result]
Or = stream_processor.Or[lexer.Token, _Result]
And = stream_processor.And[lexer.Token, _Result]
ZeroOrMore = stream_processor.ZeroOrMore[lexer.Token, _Result]
OneOrMore = stream_processor.OneOrMore[lexer.Token, _Result]
ZeroOrOne = stream_processor.ZeroOrOne[lexer.Token, _Result]
UntilEmpty = stream_processor.UntilEmpty[lexer.Token, _Result]
HeadRule = stream_processor.HeadRule[lexer.Token, _Result]


@dataclass(frozen=True)
class TokenValueRule(HeadRule[_Result]):
    rule_name: str
    func: Callable[[str], _Result]

    def result(self, head: lexer.Token) -> _Result:
        if head.rule_name != self.rule_name:
            raise errors.Error(
                msg=f'token rule_name mismatch: expected {self.rule_name} got {head.rule_name}')
        return self.func(head.value)


@dataclass(frozen=True)
class Parser(stream_processor.Processor[lexer.Token, _Result]):
    lexer_: lexer.Lexer

    def apply_str(self, input_str: str) -> StateAndResult[_Result]:
        lexer_result = self.lexer_.apply_state(
            lexer.load_char_stream(input_str)
        ).result
        return self.apply_state(lexer_result)
