from typing import Sequence, Tuple
import unittest
from . import errors, regex

_Char = regex.Char
_CharStream = regex.CharStream[_Char]
_Rule = regex.Rule[_Char]
_Scope = regex.Scope[_Char]
_StateAndResult = regex.StateAndResult[_Char]
_Literal = regex.Literal[_Char]
_Class = regex.Class[_Char]
_Range = regex.Range[_Char]
_Any = regex.Any[_Char]
_Or = regex.Or[_Char]
_Not = regex.Not[_Char]
_And = regex.And[_Char]
_ZeroOrMore = regex.ZeroOrMore[_Char]
_OneOrMore = regex.OneOrMore[_Char]
_ZeroOrOne = regex.ZeroOrOne[_Char]
_UntilEmpty = regex.UntilEmpty[_Char]


class CharTest(unittest.TestCase):
    def test_ctor_fail(self):
        for value in list[str]([
            '',
            'aa',
        ]):
            with self.subTest(value=value):
                with self.assertRaises(errors.Error):
                    _Char(value)


class TokenTest(unittest.TestCase):
    def test_add(self):
        for lhs, rhs, result in list[Tuple[regex.Token, regex.Token, regex.Token]]([
            (regex.Token(''), regex.Token(''), regex.Token('')),
            (regex.Token('a'), regex.Token(''), regex.Token('a')),
            (regex.Token(''), regex.Token('a'), regex.Token('a')),
            (regex.Token('a'), regex.Token('b'), regex.Token('ab')),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs, result=result):
                self.assertEqual(lhs + rhs, result)


class LiteralTest(unittest.TestCase):
    def test_ctor_fail(self):
        for value in list[str]([
            '',
            'aa',
        ]):
            with self.subTest(value=value):
                with self.assertRaises(errors.Error):
                    _Literal(value)

    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('a')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    _Literal('a')(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
            _CharStream([_Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Literal('a')(_Scope({}), state)


class ClassTest(unittest.TestCase):
    def test_ctor_fail(self):
        for value in list[Sequence[str]]([
            [''],
            ['aa'],
        ]):
            with self.subTest(value=value):
                with self.assertRaises(errors.Error):
                    _Class(value)

    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('a')),
            ),
            (
                _CharStream([_Char('b')]),
                (_CharStream(), regex.Token('b')),
            ),
            (
                _CharStream([_Char('b'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('b')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    _Class('ab')(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
            _CharStream([_Char('c')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Class('ab')(_Scope({}), state)


class RangeTest(unittest.TestCase):
    def test_ctor_fail(self):
        for min, max in list[Tuple[str, str]]([
            ('a', ''),
            ('aa', 'b'),
            ('', 'b'),
            ('a', 'bb'),
            ('b', 'a'),
        ]):
            with self.subTest(min=min, max=max):
                with self.assertRaises(errors.Error):
                    _Range(min, max)

    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('a')),
            ),
            (
                _CharStream([_Char('b')]),
                (_CharStream(), regex.Token('b')),
            ),
            (
                _CharStream([_Char('b'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('b')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    _Range('a', 'b')(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
            _CharStream([_Char('c')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Range('a', 'b')(_Scope({}), state)


class OrTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('a')),
            ),
            (
                _CharStream([_Char('b')]),
                (_CharStream(), regex.Token('b')),
            ),
            (
                _CharStream([_Char('b'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('b')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    _Or([
                        _Literal('a'),
                        _Literal('b'),
                    ])(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
            _CharStream([_Char('c')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Or([
                        _Literal('a'),
                        _Literal('b'),
                    ])(_Scope({}), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a'), _Char('b')]),
                (_CharStream(), regex.Token('ab')),
            ),
            (
                _CharStream([_Char('a'), _Char('b'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('ab')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    regex.And([
                        _Literal('a'),
                        _Literal('b'),
                    ])(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
            _CharStream([_Char('a')]),
            _CharStream([_Char('a'), _Char('c')]),
            _CharStream([_Char('c')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.And([
                        _Literal('a'),
                        _Literal('b'),
                    ])(_Scope({}), state)


class ZeroOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream(),
                (_CharStream(), regex.Token('')),
            ),
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('a')]),
                (_CharStream(), regex.Token('aa')),
            ),
            (
                _CharStream([_Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('')),
            ),
            (
                _CharStream([_Char('a'), _Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('a'), _Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('aa')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    regex.ZeroOrMore(
                        _Literal('a')
                    )(_Scope({}), state),
                    result
                )


class OneOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('a')]),
                (_CharStream(), regex.Token('aa')),
            ),
            (
                _CharStream([_Char('a'), _Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('a'), _Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('aa')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    regex.OneOrMore(
                        _Literal('a')
                    )(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
            _CharStream([_Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.OneOrMore(
                        _Literal('a')
                    )(_Scope({}), state)


class ZeroOrOneTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream(),
                (_CharStream(), regex.Token('')),
            ),
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('')),
            ),
            (
                _CharStream([_Char('a'), _Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('a')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    regex.ZeroOrOne(
                        _Literal('a')
                    )(_Scope({}), state),
                    result
                )


class UntilEmptyTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream(),
                (_CharStream(), regex.Token('')),
            ),
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('a')]),
                (_CharStream(), regex.Token('aa')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    regex.UntilEmpty(
                        _Literal('a')
                    )(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([_Char('b')]),
            _CharStream([_Char('a'), _Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.UntilEmpty(
                        _Literal('a')
                    )(_Scope({}), state)


class NotTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('b')]),
                (_CharStream(), regex.Token('b')),
            ),
            (
                _CharStream([_Char('b'), _Char('c')]),
                (_CharStream([_Char('c')]), regex.Token('b')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    regex.Not(
                        _Literal('a')
                    )(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
            _CharStream([_Char('a')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.Not(
                        _Literal('a')
                    )(_Scope({}), state)


class AnyTest(unittest.TestCase):
    def test_apply(self):
        for state, result in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                (_CharStream(), regex.Token('a')),
            ),
            (
                _CharStream([_Char('a'), _Char('b')]),
                (_CharStream([_Char('b')]), regex.Token('a')),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    _Any()(_Scope({}), state),
                    result
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream(),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Any()(_Scope({}), state)


class LoadTest(unittest.TestCase):
    def test_load(self):
        for input, result in list[Tuple[str, _Rule]]([
            ('a', _Literal('a')),
            ('.', _Any()),
            ('[a-z]', _Range('a', 'z')),
            ('\\w', _Class.whitespace()),
            ('\\.', _Literal('.')),
            (
                'a.\\w[0-9]',
                _And([
                    _Literal('a'),
                    _Any(),
                    _Class.whitespace(),
                    _Range('0', '9'),
                ])
            ),
            ('ab', _And([_Literal('a'), _Literal('b')])),
            ('(ab)', _And([_Literal('a'), _Literal('b')])),
            ('(a|b)', _Or([_Literal('a'), _Literal('b')])),
            ('a*', _ZeroOrMore(_Literal('a'))),
            ('a+', _OneOrMore(_Literal('a'))),
            ('a?', _ZeroOrOne(_Literal('a'))),
            ('a!', _UntilEmpty(_Literal('a'))),
            ('^a', _Not(_Literal('a'))),
        ]):
            with self.subTest(input=input, result=result):
                self.assertEqual(regex.load(input), result)

    def test_load_fail(self):
        for input in list[str]([
            '\\',
            '\\a',
            'ab[',
        ]):
            with self.subTest(input=input):
                with self.assertRaises(errors.Error):
                    regex.load(input)
