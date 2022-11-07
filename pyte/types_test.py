from dataclasses import dataclass
from typing import Tuple
import unittest
from . import errors, types_


@dataclass(frozen=True)
class _Type(types_.Type):
    _name: str

    @property
    def name(self) -> str:
        return self._name


class TypeTest(unittest.TestCase):
    def test_check_assignable(self):
        _Type('a').check_assignable(_Type('a'))

    def test_check_assignable_fail(self):
        with self.assertRaises(errors.Error):
            _Type('a').check_assignable(_Type('b'))


class ParamsTest(unittest.TestCase):
    def test_len(self):
        for params, value in list[Tuple[types_.Params, int]]([
            (types_.Params(), 0),
            (types_.Params([types_.Param('a', _Type('a'))]), 1),
            (
                types_.Params([
                    types_.Param('a', _Type('a')),
                    types_.Param('b', _Type('b')),
                ]),
                2
            ),
        ]):
            with self.subTest(params=params, value=value):
                self.assertEqual(len(params), value)

    def test_bool(self):
        for params, value in list[Tuple[types_.Params, bool]]([
            (types_.Params(), False),
            (types_.Params([types_.Param('a', _Type('a'))]), True),
        ]):
            with self.subTest(params=params, value=value):
                self.assertEqual(len(params), value)


class SignatureTest(unittest.TestCase):
    def test_eq(self):
        for lhs, rhs in list[Tuple[types_.Signature, types_.Signature]]([
            (
                types_.Signature(types_.Params(), _Type('r')),
                types_.Signature(types_.Params(), _Type('r')),
            ),
            (
                types_.Signature(
                    types_.Params([
                        types_.Param('a', _Type('A')),
                    ]),
                    _Type('r')
                ),
                types_.Signature(
                    types_.Params([
                        types_.Param('a', _Type('A')),
                    ]),
                    _Type('r')
                ),
            ),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs):
                self.assertEqual(lhs, rhs)

    def test_neq(self):
        for lhs, rhs in list[Tuple[types_.Signature, types_.Signature]]([
            (
                types_.Signature(types_.Params(), _Type('r')),
                types_.Signature(types_.Params(), _Type('s')),
            ),
            (
                types_.Signature(types_.Params(), _Type('r')),
                types_.Signature(
                    types_.Params([
                        types_.Param('a', _Type('A')),
                    ]),
                    _Type('r')
                ),
            ),
            (
                types_.Signature(
                    types_.Params([
                        types_.Param('a', _Type('A')),
                    ]),
                    _Type('r')
                ),
                types_.Signature(
                    types_.Params([
                        types_.Param('a', _Type('B')),
                    ]),
                    _Type('r')
                ),
            ),
            (
                types_.Signature(
                    types_.Params([
                        types_.Param('a', _Type('A')),
                    ]),
                    _Type('r')
                ),
                types_.Signature(
                    types_.Params([
                        types_.Param('b', _Type('A')),
                    ]),
                    _Type('r')
                ),
            ),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs):
                self.assertNotEqual(lhs, rhs)


class SignaturesTest(unittest.TestCase):
    def test_len(self):
        for signatures, value in list[Tuple[types_.Signatures, int]]([
            (
                types_.Signatures(),
                0
            ),
            (
                types_.Signatures([
                    types_.Signature(types_.Params(), _Type('r')),
                ]),
                1
            ),
        ]):
            with self.subTest(signatures=signatures, value=value):
                self.assertEqual(len(signatures), value)

    def test_bool(self):
        for signatures, value in list[Tuple[types_.Signatures, bool]]([
            (
                types_.Signatures(),
                False
            ),
            (
                types_.Signatures([
                    types_.Signature(types_.Params(), _Type('r')),
                ]),
                True
            ),
        ]):
            with self.subTest(signatures=signatures, value=value):
                self.assertEqual(bool(signatures), value)


class MutableScopeTest(unittest.TestCase):
    def test_set(self):
        types_.MutableScope({'a': types_.Var(_Type('a'))})[
            'a'] = types_.Var(_Type('a'))

    def test_set_fail(self):
        with self.assertRaises(errors.Error):
            types_.MutableScope({'a': types_.Var(_Type('a'))})[
                'a'] = types_.Var(_Type('b'))
