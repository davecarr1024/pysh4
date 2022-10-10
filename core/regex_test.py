from typing import Sequence, Tuple
import unittest
from . import errors, regex

_Char = regex.Char
_CharStream = regex.CharStream[_Char]
_StateAndResult = regex.StateAndResult[_Char]
_Scope = regex.Scope[_Char]
_Literal = regex.Literal[_Char]
_Class = regex.Class[_Char]
_Range = regex.Range[_Char]
_Regex = regex.Regex[_Char]
_Not = regex.Not[_Char]


class CharTest(unittest.TestCase):
    def test_ctor(self):
        regex.Char('a')

    def test_ctor_fail(self):
        for value in list[str]([
            '',
            'aa',
        ]):
            with self.subTest(value=value):
                with self.assertRaises(errors.Error):
                    regex.Char(value)


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
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([regex.Char('a')]),
                _StateAndResult(_CharStream([]), 'a'),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                _StateAndResult(
                    _CharStream([
                        regex.Char('b'),
                    ]),
                    'a'
                ),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _Literal('a').apply(
                        _Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([]),
            _CharStream([regex.Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Literal('a').apply(
                        _Scope({}), state)


class ClassTest(unittest.TestCase):
    def test_ctor_fail(self):
        for values in list[Sequence[str]]([
            [],
            ['aa'],
            ['a', 'bb'],
        ]):
            with self.subTest(values=values):
                with self.assertRaises(errors.Error):
                    regex.Class(values)

    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                _StateAndResult(_CharStream([]), 'a'),
            ),
            (
                _CharStream([_Char('b')]),
                _StateAndResult(_CharStream([]), 'b'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _Class(['a', 'b']).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([]),
            _CharStream([_Char('c')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Class(['a', 'b']).apply(_Scope({}), state)


class RangeTest(unittest.TestCase):
    def test_ctor_fail(self):
        for min, max in list[Tuple[str, str]]([
            ('aa', 'b'),
            ('a', 'bb'),
            ('b', 'a'),
        ]):
            with self.subTest(min=min, max=max):
                with self.assertRaises(errors.Error):
                    regex.Range(min, max)

    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('a')]),
                _StateAndResult(_CharStream([]), 'a'),
            ),
            (
                _CharStream([_Char('b')]),
                _StateAndResult(_CharStream([]), 'b'),
            ),
            (
                _CharStream([_Char('c')]),
                _StateAndResult(_CharStream([]), 'c'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _Range('a', 'c').apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([]),
            _CharStream([_Char('d')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Range('a', 'c').apply(_Scope({}), state)


class NotTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([_Char('b')]),
                _StateAndResult(_CharStream([]), 'b'),
            ),
            (
                _CharStream([_Char('b'), _Char('a')]),
                _StateAndResult(_CharStream([_Char('a')]), 'b'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _Not(_Literal('a')).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([]),
            _CharStream([_Char('a')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Not(_Literal('a')).apply(_Scope({}), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                _StateAndResult(_CharStream([]), 'ab'),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                    regex.Char('c'),
                ]),
                _StateAndResult(
                    _CharStream([
                        regex.Char('c'),
                    ]),
                    'ab'
                ),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.And([
                        _Literal('a'),
                        _Literal('b'),
                    ]).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([]),
            _CharStream([regex.Char('b')]),
            _CharStream([
                regex.Char('a'),
                regex.Char('c'),
            ]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.And([
                        _Literal('a'),
                        _Literal('b'),
                    ]).apply(_Scope({}), state)


class ZeroOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([]),
                _StateAndResult(_CharStream([]), ''),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                ]),
                _StateAndResult(_CharStream([]), 'a'),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                ]),
                _StateAndResult(_CharStream([]), 'aa'),
            ),
            (
                _CharStream([
                    regex.Char('b'),
                ]),
                _StateAndResult(_CharStream([regex.Char('b')]), ''),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                _StateAndResult(_CharStream([regex.Char('b')]), 'a'),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                _StateAndResult(
                    _CharStream([regex.Char('b')]), 'aa'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.ZeroOrMore(
                        _Literal('a'),
                    ).apply(_Scope({}), state),
                    expected_output
                )


class OneOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                ]),
                _StateAndResult(_CharStream([]), 'aa'),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                _StateAndResult(_CharStream([regex.Char('b')]), 'a'),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                _StateAndResult(
                    _CharStream([regex.Char('b')]), 'aa'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.OneOrMore(
                        _Literal('a'),
                    ).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([]),
            _CharStream([regex.Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.OneOrMore(
                        _Literal('a')
                    ).apply(_Scope({}), state)


class ZeroOrOneTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([]),
                _StateAndResult(_CharStream([]), ''),
            ),
            (
                _CharStream([regex.Char('a')]),
                _StateAndResult(_CharStream([]), 'a'),
            ),
            (
                _CharStream([regex.Char('b')]),
                _StateAndResult(_CharStream([regex.Char('b')]), ''),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                _StateAndResult(_CharStream([regex.Char('b')]), 'a'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.ZeroOrOne(
                        _Literal('a')
                    ).apply(_Scope({}), state),
                    expected_output
                )


class UntilEmptyTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_CharStream, _StateAndResult]]([
            (
                _CharStream([
                ]),
                _StateAndResult(_CharStream([]), ''),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                ]),
                _StateAndResult(_CharStream([]), 'a'),
            ),
            (
                _CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                ]),
                _StateAndResult(_CharStream([]), 'aa'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.UntilEmpty(
                        _Literal('a'),
                    ).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_CharStream]([
            _CharStream([regex.Char('b')]),
            _CharStream([
                regex.Char('a'),
                regex.Char('b'),
            ]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.UntilEmpty(
                        _Literal('a')
                    ).apply(_Scope({}), state)


class RegexTest(unittest.TestCase):
    def test_load(self):
        for input_str, regex_ in list[Tuple[str, _Regex]]([
            ('a', regex.Regex(regex.Literal('a'))),
        ]):
            with self.subTest(input_str=input_str, regex_=regex_):
                self.assertEqual(
                    regex.Regex.load(input_str),
                    regex_
                )