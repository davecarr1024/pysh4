from typing import Tuple
import unittest
from . import errors, regex


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
    def test_apply(self):
        for state, expected_output in list[Tuple[regex.CharStream, regex.StateAndResult]]([
            (
                regex.CharStream([regex.Char('a')]),
                regex.StateAndResult(regex.CharStream([]), 'a'),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                regex.StateAndResult(
                    regex.CharStream([
                        regex.Char('b'),
                    ]),
                    'a'
                ),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.Literal(regex.Char('a')).apply(
                        regex.Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[regex.CharStream]([
            regex.CharStream([]),
            regex.CharStream([regex.Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.Literal(regex.Char('a')).apply(
                        regex.Scope({}), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[regex.CharStream, regex.StateAndResult]]([
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                regex.StateAndResult(regex.CharStream([]), 'ab'),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                    regex.Char('c'),
                ]),
                regex.StateAndResult(
                    regex.CharStream([
                        regex.Char('c'),
                    ]),
                    'ab'
                ),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.And([
                        regex.Literal(regex.Char('a')),
                        regex.Literal(regex.Char('b')),
                    ]).apply(regex.Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[regex.CharStream]([
            regex.CharStream([]),
            regex.CharStream([regex.Char('b')]),
            regex.CharStream([
                regex.Char('a'),
                regex.Char('c'),
            ]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.And([
                        regex.Literal(regex.Char('a')),
                        regex.Literal(regex.Char('b')),
                    ]).apply(regex.Scope({}), state)


class ZeroOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[regex.CharStream, regex.StateAndResult]]([
            (
                regex.CharStream([]),
                regex.StateAndResult(regex.CharStream([]), ''),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                ]),
                regex.StateAndResult(regex.CharStream([]), 'a'),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                ]),
                regex.StateAndResult(regex.CharStream([]), 'aa'),
            ),
            (
                regex.CharStream([
                    regex.Char('b'),
                ]),
                regex.StateAndResult(regex.CharStream([regex.Char('b')]), ''),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                regex.StateAndResult(regex.CharStream([regex.Char('b')]), 'a'),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                regex.StateAndResult(
                    regex.CharStream([regex.Char('b')]), 'aa'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.ZeroOrMore(
                        regex.Literal(regex.Char('a')),
                    ).apply(regex.Scope({}), state),
                    expected_output
                )


class OneOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[regex.CharStream, regex.StateAndResult]]([
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                ]),
                regex.StateAndResult(regex.CharStream([]), 'aa'),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                regex.StateAndResult(regex.CharStream([regex.Char('b')]), 'a'),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                regex.StateAndResult(
                    regex.CharStream([regex.Char('b')]), 'aa'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.OneOrMore(
                        regex.Literal(regex.Char('a')),
                    ).apply(regex.Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[regex.CharStream]([
            regex.CharStream([]),
            regex.CharStream([regex.Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.OneOrMore(
                        regex.Literal(regex.Char('a'))
                    ).apply(regex.Scope({}), state)


class ZeroOrOneTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[regex.CharStream, regex.StateAndResult]]([
            (
                regex.CharStream([]),
                regex.StateAndResult(regex.CharStream([]), ''),
            ),
            (
                regex.CharStream([regex.Char('a')]),
                regex.StateAndResult(regex.CharStream([]), 'a'),
            ),
            (
                regex.CharStream([regex.Char('b')]),
                regex.StateAndResult(regex.CharStream([regex.Char('b')]), ''),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('b'),
                ]),
                regex.StateAndResult(regex.CharStream([regex.Char('b')]), 'a'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.ZeroOrOne(
                        regex.Literal(regex.Char('a'))
                    ).apply(regex.Scope({}), state),
                    expected_output
                )


class UntilEmptyTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[regex.CharStream, regex.StateAndResult]]([
            (
                regex.CharStream([
                ]),
                regex.StateAndResult(regex.CharStream([]), ''),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                ]),
                regex.StateAndResult(regex.CharStream([]), 'a'),
            ),
            (
                regex.CharStream([
                    regex.Char('a'),
                    regex.Char('a'),
                ]),
                regex.StateAndResult(regex.CharStream([]), 'aa'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    regex.UntilEmpty(
                        regex.Literal(regex.Char('a')),
                    ).apply(regex.Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[regex.CharStream]([
            regex.CharStream([regex.Char('b')]),
            regex.CharStream([
                regex.Char('a'),
                regex.Char('b'),
            ]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    regex.UntilEmpty(
                        regex.Literal(regex.Char('a'))
                    ).apply(regex.Scope({}), state)
