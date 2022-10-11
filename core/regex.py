from dataclasses import dataclass
import string
from typing import Collection, Mapping, Sequence, Tuple, TypeVar
from . import errors, stream_processor


@dataclass(frozen=True)
class Char:
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid char value {repr(self.value)}')


_Char = TypeVar('_Char', bound=Char)

RuleError = stream_processor.RuleError[_Char, str]
CharStream = stream_processor.Stream[_Char]
StateAndResult = stream_processor.StateAndResult[_Char, str]
Rule = stream_processor.Rule[_Char, str]
Scope = stream_processor.Scope[_Char, str]
Ref = stream_processor.Ref[_Char, str]
Or = stream_processor.Or[_Char, str]
UnaryRule = stream_processor.UnaryRule[_Char, str]
NaryRule = stream_processor.NaryRule[_Char, str]
_HeadRule = stream_processor.HeadRule[_Char, str]

_ROOT_RULE_NAME = '_root'


class ResultCombiner(stream_processor.ResultCombiner[str]):
    def combine_results(self, results: Sequence[str]) -> str:
        return ''.join(results)


class And(stream_processor.And[_Char, str], ResultCombiner):
    ...


class ZeroOrMore(stream_processor.ZeroOrMore[_Char, str], ResultCombiner):
    ...


class OneOrMore(stream_processor.OneOrMore[_Char, str], ResultCombiner):
    ...


class ZeroOrOne(stream_processor.ZeroOrOne[_Char, str], ResultCombiner):
    ...


class UntilEmpty(stream_processor.UntilEmpty[_Char, str], ResultCombiner):
    ...


@dataclass(frozen=True, repr=False)
class Literal(_HeadRule[_Char]):
    value: str

    def __post_init__(self):
        if len(self.value) != 1:
            raise errors.Error(msg=f'invalid literal value {repr(self.value)}')

    def __repr__(self) -> str:
        return repr(self.value)

    def result(self, head: _Char) -> str:
        if self.value != head.value:
            raise errors.Error(msg=f'head {head} != literal {self}')
        return head.value


@dataclass(frozen=True, repr=False)
class Class(_HeadRule[_Char]):
    values: Collection[str]

    def __post_init__(self):
        if len(self.values) == 0:
            raise errors.Error(msg='empty class')
        for value in self.values:
            if len(value) != 1:
                raise errors.Error(msg=f'invalid class value {repr(value)}')

    def __repr__(self) -> str:
        return repr(self.values)

    def result(self, head: _Char) -> str:
        if head.value not in self.values:
            raise errors.Error(msg=f'head {head} not in class {self}')
        return head.value

    @staticmethod
    def whitespace() -> 'Class[_Char]':
        return Class[_Char](string.whitespace)

    @staticmethod
    def classes() -> Mapping[str, 'Class[_Char]']:
        return {'w': Class.whitespace()}


@dataclass(frozen=True)
class Range(_HeadRule[_Char]):
    min: str
    max: str

    def __post_init__(self):
        if len(self.min) != 1:
            raise errors.Error(msg=f'invalid min {self.min}')
        if len(self.max) != 1:
            raise errors.Error(msg=f'invalid max {self.max}')
        if self.max < self.min:
            raise errors.Error(msg=f'invalid range {self}')

    def __repr__(self) -> str:
        return f'[{self.min}-{self.max}]'

    def result(self, head: _Char) -> str:
        if head.value < self.min or head.value > self.max:
            raise errors.Error(msg=f'head {head} not in range {self}')
        return head.value


@dataclass(frozen=True)
class Not(UnaryRule[_Char]):
    def __repr__(self) -> str:
        return f'^{self.child}'

    def apply(self, scope: Scope[_Char], state: CharStream[_Char]) -> StateAndResult[_Char]:
        if state.empty:
            raise RuleError[_Char](
                rule=self, state=state, msg='empty stream', children=[])
        try:
            self.child.apply(scope, state)
        except errors.Error:
            return StateAndResult[_Char](state.tail, state.head.value)
        raise RuleError[_Char](
            rule=self, state=state, msg='applied negated rule', children=[])


@dataclass(frozen=True)
class Any(_HeadRule[_Char]):
    def __repr__(self) -> str:
        return '.'

    def result(self, head: _Char) -> str:
        return head.value


def load(input_str: str) -> 'Rule[_Char]':
    from . import lexer, parser

    operators = '()[]-+?*!^.\\'

    _Rule = Rule[_Char]
    Or = parser.Or[_Rule]
    Ref = parser.Ref[_Rule]
    TokenValueRule = parser.TokenValueRule[_Rule]

    def consume_token(state: lexer.TokenStream, rule_name: str) -> lexer.TokenStream:
        state, _ = token_value(state, rule_name)
        return state

    def token_value(state: lexer.TokenStream, rule_name: str) -> Tuple[lexer.TokenStream, str]:
        if state.empty:
            raise parser.StateError(
                state=state, children=[], msg=f'empty stream')
        if state.head.rule_name != rule_name:
            raise parser.StateError(state=state, children=[],
                                    msg=f'expected rule_name {rule_name} got {state.head.rule_name}')
        return state.tail, state.head.value

    class RangeLoader(parser.Rule[_Rule]):
        def apply(self, scope: parser.Scope[_Rule], state: lexer.TokenStream) -> parser.StateAndResult[_Rule]:
            state = consume_token(state, '[')
            state, min = token_value(state, 'char')
            state = consume_token(state, '-')
            state, max = token_value(state, 'char')
            state = consume_token(state, ']')
            return parser.StateAndResult[_Rule](state, Range(min, max))

    class SpecialLoader(parser.Rule[_Rule]):
        def apply(self, scope: parser.Scope[_Rule], state: lexer.TokenStream) -> parser.StateAndResult[_Rule]:
            state = consume_token(state, '\\')
            value = state.head.value
            if value in Class.classes():
                return parser.StateAndResult[_Rule](state.tail, Class[_Char].classes()[value])
            if value in operators:
                return parser.StateAndResult[_Rule](state.tail, Literal[_Char](value))
            raise parser.RuleError[_Rule](
                rule=self, state=state, msg=f'invalid special value {repr(value)}', children=[])

    return parser.Parser[Rule[_Char]](
        {
            'rule': Or([
                Ref('operation'),
                Ref('operand'),
            ]),
            'operand': Or([
                Ref('literal'),
                Ref('any'),
                Ref('range'),
                Ref('special'),
            ]),
            'literal': TokenValueRule('char', lambda value: Literal(value)),
            'any': TokenValueRule('.', lambda _: Any()),
            'range': RangeLoader(),
            'special': SpecialLoader(),
        },
        'rule',
        lexer.Lexer([
            lexer.Regex(
                'char',
                Not(Class(operators)),
            ),
            *[lexer.Regex(operator, Literal(operator)) for operator in operators]
        ])
    ).apply_str(input_str).result
