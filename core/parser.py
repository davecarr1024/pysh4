from typing import TypeVar
from . import lexer, processor

_Result = TypeVar('_Result')

Rule = processor.Rule[lexer.TokenStream, _Result]
Scope = processor.Scope[lexer.TokenStream, _Result]
StateAndResult = processor.StateAndResult[lexer.TokenStream, _Result]
