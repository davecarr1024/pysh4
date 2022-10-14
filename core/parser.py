from typing import TypeVar
from . import lexer, processor, stream

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
Parser = processor.Processor[lexer.TokenStream, _Result]
