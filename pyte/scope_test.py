from dataclasses import dataclass
from typing import Mapping, Tuple
import unittest
from . import errors, scope


@dataclass
class _Var:
    value: int


_Scope = scope.Scope[_Var]


class _MutableScope(scope.MutableScope[_Var]):
    @classmethod
    def set(cls, lhs: _Var, rhs: _Var) -> None:
        lhs.value = rhs.value


class ScopeTest(unittest.TestCase):
    def test_eq(self):
        for lhs, rhs in list[Tuple[_Scope, _Scope]]([
            (_Scope(), _Scope()),
            (
                _Scope({'a': _Var(1)}),
                _Scope({'a': _Var(1)}),
            ),
            (
                _Scope({'a': _Var(1)}),
                _Scope({}, parent=_Scope({'a': _Var(1)})),
            ),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs):
                self.assertEqual(lhs, rhs)

    def test_neq(self):
        for lhs, rhs in list[Tuple[_Scope, _Scope]]([
            (_Scope(), _Scope({'a': _Var(1)})),
            (
                _Scope({'a': _Var(1)}),
                _Scope({'a': _Var(2)}),
            ),
            (
                _Scope({'a': _Var(1)}),
                _Scope({}, parent=_Scope({'a': _Var(2)})),
            ),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs):
                self.assertNotEqual(lhs, rhs)

    def test_vars(self):
        for scope, vars in list[Tuple[_Scope, Mapping[str, _Var]]]([
            (
                _Scope(),
                {}
            ),
            (
                _Scope({'a': _Var(1)}),
                {'a': _Var(1)}
            ),
            (
                _Scope({'a': _Var(1), 'b': _Var(2)}),
                {'a': _Var(1), 'b': _Var(2)}
            ),
            (
                _Scope({'a': _Var(1)}, parent=_Scope({'b': _Var(2)})),
                {'a': _Var(1)}
            ),
        ]):
            with self.subTest(scope=scope, vars=vars):
                self.assertDictEqual(scope.vars, vars)

    def test_all_vars(self):
        for scope, vars in list[Tuple[_Scope, Mapping[str, _Var]]]([
            (
                _Scope(),
                {}
            ),
            (
                _Scope({'a': _Var(1)}),
                {'a': _Var(1)}
            ),
            (
                _Scope({'a': _Var(1), 'b': _Var(2)}),
                {'a': _Var(1), 'b': _Var(2)}
            ),
            (
                _Scope({'a': _Var(1)}, parent=_Scope({'b': _Var(2)})),
                {'a': _Var(1), 'b': _Var(2)}
            ),
            (
                _Scope({'a': _Var(1), 'b': _Var(2)},
                       parent=_Scope({'b': _Var(3)})),
                {'a': _Var(1), 'b': _Var(2)}
            ),
        ]):
            with self.subTest(scope=scope, vars=vars):
                self.assertDictEqual(scope.all_vars, vars)

    def test_as_child(self):
        self.assertEqual(
            _Scope({'a': _Var(1)}).as_child(),
            _Scope({}, parent=_Scope({'a': _Var(1)}))
        )

    def test_getitem_fail(self):
        with self.assertRaises(errors.Error):
            _Scope()['a']


class MutableScopeTest(unittest.TestCase):
    def test_decl(self):
        scope = _MutableScope()
        self.assertNotIn('a', scope)
        scope.decl('a', _Var(1))
        self.assertEqual(scope['a'], _Var(1))

    def test_decl_fail(self):
        with self.assertRaises(errors.Error):
            _MutableScope({'a': _Var(1)}).decl('a', _Var(2))

    def test_set(self):
        scope = _MutableScope({'a': _Var(1)})
        self.assertEqual(scope['a'], _Var(1))
        scope['a'] = _Var(2)
        self.assertEqual(scope['a'], _Var(2))

    def test_set_fail(self):
        with self.assertRaises(errors.Error):
            _MutableScope()['a'] = _Var(1)

    def test_del(self):
        scope = _MutableScope({'a': _Var(1)})
        self.assertEqual(scope['a'], _Var(1))
        del scope['a']
        self.assertNotIn('a', scope)

    def test_del_fail(self):
        with self.assertRaises(errors.Error):
            del _MutableScope()['a']
