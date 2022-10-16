from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

from . import errors, processor, stream


@dataclass(frozen=True)
class Char:
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid value {self.value}')

    def __repr__(self) -> str:
        return repr(self.value)


_Char = TypeVar('_Char', bound=Char, covariant=True)

CharStream = stream.Stream[_Char]


@dataclass(frozen=True)
class Token:
    value: str

    def __add__(self, rhs: 'Token') -> 'Token':
        return Token(self.value + rhs.value)

    @staticmethod
    def concat(tokens: Sequence['Token']) -> 'Token':
        return sum(tokens, Token(''))


RuleError = processor.RuleError[CharStream[_Char], Token]
Rule = processor.Rule[CharStream[_Char], Token]
NaryRule = processor.NaryRule[CharStream[_Char], Token]
MultipleResultRule = processor.MultipleResultRule[CharStream[_Char], Token]
Scope = processor.Scope[CharStream[_Char], Token]
StateAndResult = processor.StateAndResult[CharStream[_Char], Token]
Ref = processor.Ref[CharStream[_Char], Token]
Or = processor.Or[CharStream[_Char], Token]


@dataclass(frozen=True, repr=False)
class _ResultCombiner(processor.ResultCombiner[CharStream[_Char], Token]):
    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        state, results = self.rule(scope, state)
        return state, Token.concat(results)


class And(_ResultCombiner[_Char]):
    def __init__(self, rules: Sequence[Rule[_Char]]):
        super().__init__(processor.And[CharStream[_Char], Token](rules))


class ZeroOrMore(_ResultCombiner[_Char]):
    def __init__(self, rule: Rule[_Char]):
        super().__init__(processor.ZeroOrMore[CharStream[_Char], Token](rule))


class OneOrMore(_ResultCombiner[_Char]):
    def __init__(self, rule: Rule[_Char]):
        super().__init__(processor.OneOrMore[CharStream[_Char], Token](rule))


class ZeroOrOne(_ResultCombiner[_Char]):
    def __init__(self, rule: Rule[_Char]):
        super().__init__(processor.ZeroOrOne[CharStream[_Char], Token](rule))


class UntilEmpty(_ResultCombiner[_Char]):
    def __init__(self, rule: Rule[_Char]):
        super().__init__(stream.UntilEmpty[CharStream[_Char], Token](rule))


@dataclass(frozen=True, repr=False)
class Literal(Generic[_Char]):
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid literal value {self.value}')

    def __repr__(self) -> str:
        return repr(self.value)

    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        if state.empty:
            raise RuleError[_Char](rule=self, state=state, msg='empty stream')
        if state.head.value != self.value:
            raise RuleError[_Char](
                rule=self, state=state, msg=f'expected {repr(self.value)} but got {state.head}')
        return state.tail, Token(state.head.value)


@dataclass(frozen=True, repr=False)
class Not(processor.UnaryRule[CharStream[_Char], Token]):
    def __repr__(self) -> str:
        return f'^{self.rule}'

    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        try:
            self.rule(scope, state)
        except errors.Error:
            return state.tail, Token(state.head.value)
        raise RuleError[_Char](rule=self, state=state,
                               msg=f'successfully applied not rule')


@dataclass(frozen=True, repr=False)
class Class(Generic[_Char]):
    values: Sequence[str]

    def __post_init__(self):
        for value in self.values:
            if len(value) != 1:
                raise errors.Error(msg=f'invalid literal value {value}')

    def __repr__(self) -> str:
        return repr(self.values)

    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        if state.empty:
            raise RuleError[_Char](rule=self, state=state, msg='empty stream')
        if state.head.value not in self.values:
            raise RuleError[_Char](
                rule=self, state=state, msg=f'expected {repr(self.values)} but got {state.head}')
        return state.tail, Token(state.head.value)


@dataclass(frozen=True, repr=False)
class Range(Generic[_Char]):
    min: str
    max: str

    def __post_init__(self):
        if len(self.min) != 1 or len(self.max) != 1 or self.max < self.min:
            raise errors.Error(msg=f'invalid range {self}')

    def __repr__(self) -> str:
        return f'[{self.min}-{self.max}]'

    def __call__(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        if state.empty:
            raise RuleError[_Char](rule=self, state=state, msg='empty stream')
        if state.head.value < self.min or state.head.value > self.max:
            raise RuleError[_Char](
                rule=self, state=state, msg=f'expected in {self} but got {state.head}')
        return state.tail, Token(state.head.value)


def load(input: str) -> Rule[_Char]:
    from . import lexer, parser

    operators = ''

    def load_root(scope: parser.Scope[Rule[_Char]], state: lexer.TokenStream) -> parser.StateAndResult[Rule[_Char]]:
        state, results = parser.UntilEmpty[Rule[_Char]](
            parser.Ref[Rule[_Char]]('rule'))(scope, state)
        if len(results) == 1:
            return state, results[0]
        return state, And(results)

    def load_literal(scope: parser.Scope[Rule[_Char]], state: lexer.TokenStream) -> parser.StateAndResult[Rule[_Char]]:
        state, value = parser.get_token_value(state, 'char')
        return state, Literal[_Char](value)

    _, result = parser.Parser[Rule[_Char]](
        {
            'root': load_root,
            'rule': parser.Or[Rule[_Char]]([
                load_literal,
            ]),
        },
        'root',
        lexer.Lexer(
            char=lexer.ReNot(lexer.ReClass(operators)),
            **{
                operator: lexer.ReLiteral(operator)
                for operator in operators
            }
        )
    )(parser.Scope[Rule[_Char]]({}), input)

    return result
