from abc import ABC, abstractmethod
from dataclasses import dataclass
import operator
from typing import Callable, Iterator, Mapping, MutableMapping, Optional, Sequence
import unittest
from . import errors, lexer, parser, regex


@dataclass(frozen=True, repr=False)
class _Scope(MutableMapping[str, '_Val']):
    _vals: MutableMapping[str, '_Val']
    _parent: Optional['_Scope'] = None

    def __repr__(self) -> str:
        return repr(self.all_vals)

    def __delitem__(self, name: str) -> None:
        del self._vals[name]

    def __getitem__(self, name: str) -> '_Val':
        if name in self._vals:
            return self._vals[name]
        if self._parent is not None:
            return self._parent[name]
        raise errors.Error(msg=f'unknown var {name}')

    def __iter__(self) -> Iterator[str]:
        return iter(self.all_vals)

    def __len__(self) -> int:
        return len(self.all_vals)

    def __setitem__(self, name: str, val: '_Val') -> None:
        self._vals[name] = val

    @property
    def vals(self) -> Mapping[str, '_Val']:
        return self._vals

    @property
    def all_vals(self) -> Mapping[str, '_Val']:
        vals: MutableMapping[str, '_Val'] = {}
        if self._parent is not None:
            vals |= self._parent.all_vals
        vals |= self.vals
        return vals

    @staticmethod
    def default() -> '_Scope':
        return _Scope(dict(_IntFunc.operators()), None)

    def as_child(self) -> '_Scope':
        return _Scope({}, self)


class ScopeTest(unittest.TestCase):
    def test_vals(self):
        self.assertDictEqual(
            _Scope(
                {
                    'b': _Int(2),
                },
                _Scope({
                    'a': _Int(1),
                })).vals,
            {'b': _Int(2)}
        )

    def test_all_vals(self):
        self.assertDictEqual(
            _Scope({
                'a': _Int(1),
            },
                _Scope({
                    'a': _Int(2),
                    'b': _Int(3),
                })
            ).all_vals,
            {
                'a': _Int(1),
                'b': _Int(3),
            }
        )


class _Val(ABC):
    def apply(self, scope: _Scope, args: Sequence['_Val']) -> '_Val':
        raise NotImplementedError(f'unapplyable val {self}')


@dataclass(frozen=True, repr=False)
class _Int(_Val):
    value: int

    def __repr__(self) -> str:
        return repr(self.value)


@dataclass(frozen=True)
class _IntFunc(_Val):
    func: Callable[[int, int], int]

    def apply(self, scope: _Scope, args: Sequence[_Val]) -> _Val:
        if len(args) != 2 or not all(isinstance(arg, _Int) for arg in args):
            raise errors.Error(msg=f'invalid args {args}')
        lhs, rhs = args
        assert isinstance(lhs, _Int) and isinstance(rhs, _Int)
        return _Int(self.func(lhs.value, rhs.value))

    @staticmethod
    def operators() -> Mapping[str, '_IntFunc']:
        return {'+': _IntFunc(operator.add)}


class IntFuncTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(
            _Scope.default()['+'].apply(_Scope({}), [_Int(1), _Int(2)]),
            _Int(3)
        )


class _Expr(ABC):
    @abstractmethod
    def eval(self, scope: _Scope) -> '_Val':
        ...

    @staticmethod
    def _loader() -> parser.Rule['_Expr']:
        return parser.Parser[_Expr](
            {

            },
            'root',
            lexer.Lexer([
                lexer.Regex('(', regex.Literal('(')),
            ])
        )


@dataclass(frozen=True, repr=False)
class _Literal(_Expr):
    value: _Val

    def __repr__(self) -> str:
        return repr(self.value)

    def eval(self, scope: _Scope) -> _Val:
        return self.value


class LiteralTest(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(_Literal(_Int(1)).eval(_Scope({})), _Int(1))


@dataclass(frozen=True, repr=False)
class _Ref(_Expr):
    name: str

    def __repr__(self) -> str:
        return self.name

    def eval(self, scope: _Scope) -> _Val:
        if self.name not in scope:
            raise errors.Error(msg=f'unknown var {self.name}')
        return scope[self.name]


class RefTest(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            _Ref('a').eval(_Scope({'a': _Int(1)})),
            _Int(1)
        )

    def test_eval_fail(self):
        with self.assertRaises(errors.Error):
            _Ref('a').eval(_Scope({}))


@dataclass(frozen=True, repr=False)
class _Call(_Expr):
    operator: _Expr
    operands: Sequence[_Expr]

    def __repr__(self) -> str:
        return f'({repr(self.operator)} {" ".join(repr(operand) for operand in self.operands)})'

    def eval(self, scope: _Scope) -> _Val:
        operator = self.operator.eval(scope)
        operands: Sequence[_Val] = [operand.eval(
            scope) for operand in self.operands]
        return operator.apply(scope, operands)
