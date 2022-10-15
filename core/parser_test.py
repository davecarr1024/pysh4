from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import string
import operator
from typing import Callable, Iterator, Mapping, Tuple
import unittest
from . import errors, lexer, parser


@dataclass(frozen=True, repr=False)
class _Int:
    value: int

    def __repr__(self) -> str:
        return repr(self.value)


@dataclass(frozen=True, repr=False)
class _Scope(Mapping[str, _Int]):
    _vals: Mapping[str, _Int]

    def __getitem__(self, name: str) -> _Int:
        if name not in self._vals:
            raise errors.Error(msg=f'unknown name {name}')
        return self._vals[name]

    def __iter__(self) -> Iterator[str]:
        return iter(self._vals)

    def __len__(self) -> int:
        return len(self._vals)


class _Expr(ABC):
    @abstractmethod
    def eval(self, scope: _Scope) -> _Int:
        ...


@dataclass(frozen=True, repr=False)
class _Literal(_Expr):
    value: _Int

    def __repr__(self) -> str:
        return repr(self.value)

    def eval(self, scope: _Scope) -> _Int:
        return self.value


@dataclass(frozen=True, repr=False)
class _Ref(_Expr):
    name: str

    def __repr__(self) -> str:
        return self.name

    def eval(self, scope: _Scope) -> _Int:
        if self.name not in scope:
            raise errors.Error(msg=f'unknown ref {self}')
        return scope[self.name]


@dataclass(frozen=True, repr=False)
class _Operation(_Expr):
    class Operator(Enum):
        ADD = '+'

    operator: Operator
    lhs: _Expr
    rhs: _Expr

    def __repr__(self) -> str:
        return f'{self.lhs} {self.operator.value} {self.rhs}'

    def eval(self, scope: _Scope) -> _Int:
        funcs: Mapping[_Operation.Operator, Callable[[int, int], int]] = {
            _Operation.Operator.ADD: operator.add,
        }
        assert self.operator in funcs, self.operator
        return _Int(funcs[self.operator](self.lhs.eval(scope).value, self.rhs.eval(scope).value))


def _load_expr(input: str) -> _Expr:
    def load_int(scope: parser.Scope[_Expr], state: lexer.TokenStream) -> parser.StateAndResult[_Expr]:
        state, value = parser.get_token_value(state, 'int')
        return state, _Literal(_Int(int(value)))

    def load_ref(scope: parser.Scope[_Expr], state: lexer.TokenStream) -> parser.StateAndResult[_Expr]:
        state, value = parser.get_token_value(state, 'id')
        return state, _Ref(value)

    def load_operation(scope: parser.Scope[_Expr], state: lexer.TokenStream) -> parser.StateAndResult[_Expr]:
        state, lhs = parser.Ref[_Expr]('operand')(scope, state)
        state, operator = parser.get_token_value(state, 'operator')
        state, rhs = parser.Ref[_Expr]('operand')(scope, state)
        return state, _Operation(_Operation.Operator(operator), lhs, rhs)

    parser_state, parser_result = parser.Parser[_Expr](
        {
            'expr': parser.Or[_Expr]([
                parser.Ref[_Expr]('operation'),
                parser.Ref[_Expr]('operand'),
            ]),
            'operation': load_operation,
            'operand': parser.Or[_Expr]([
                parser.Ref[_Expr]('int'),
                parser.Ref[_Expr]('ref'),
            ]),
            'int': load_int,
            'ref': load_ref,
        },
        'expr',
        lexer.Lexer(
            _ws=lexer.ReClass(string.whitespace),
            int=lexer.ReOneOrMore(
                lexer.ReClass(string.digits)),
            id=lexer.ReOneOrMore(
                lexer.ReOr([
                    lexer.ReLiteral('_'),
                    lexer.ReRange('a', 'z'),
                    lexer.ReRange('A', 'Z'),
                ])
            ),
            operator=lexer.ReOr([
                lexer.ReLiteral(operator.value)
                for operator in _Operation.Operator
            ]),
        )

    )(parser.Scope[_Expr]({}), input)

    if not parser_state.empty:
        raise errors.Error(msg=f'leftover state {parser_state}')
    return parser_result


class LoadTest(unittest.TestCase):
    def test_load(self):
        for input, expr in list[Tuple[str, _Expr]]([
            ('1', _Literal(_Int(1))),
            ('a', _Ref('a')),
            (
                '1 + 2',
                _Operation(
                    _Operation.Operator.ADD,
                    _Literal(_Int(1)),
                    _Literal(_Int(2)),
                ),
            ),
        ]):
            with self.subTest(input=input, expr=expr):
                self.assertEqual(_load_expr(input), expr)

    def test_eval(self):
        for input, val in list[Tuple[str, _Int]]([
            ('1', _Int(1)),
            ('a', _Int(1)),
            ('1 + 2', _Int(3)),
        ]):
            with self.subTest(input=input, val=val):
                self.assertEqual(
                    _load_expr(input).eval(_Scope({
                        'a': _Int(1),
                    })),
                    val
                )
