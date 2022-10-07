from typing import Tuple
import unittest
from . import errors, lexer_rule


class CharTest(unittest.TestCase):
    def test_ctor(self):
        lexer_rule.Char('a')

    def test_ctor_fail(self):
        for value in list[str]([
            '',
            'aa',
        ]):
            with self.subTest(value=value):
                with self.assertRaises(errors.Error):
                    lexer_rule.Char(value)


class LiteralTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[lexer_rule.CharStream, lexer_rule.StateAndResult]]([
            (
                lexer_rule.CharStream([lexer_rule.Char('a')]),
                lexer_rule.StateAndResult(lexer_rule.CharStream([]), 'a'),
            ),
            (
                lexer_rule.CharStream([
                    lexer_rule.Char('a'),
                    lexer_rule.Char('b'),
                ]),
                lexer_rule.StateAndResult(
                    lexer_rule.CharStream([
                        lexer_rule.Char('b'),
                    ]),
                    'a'
                ),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    lexer_rule.Literal(lexer_rule.Char('a')).apply(
                        lexer_rule.Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[lexer_rule.CharStream]([
            lexer_rule.CharStream([]),
            lexer_rule.CharStream([lexer_rule.Char('b')]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    lexer_rule.Literal(lexer_rule.Char('a')).apply(
                        lexer_rule.Scope({}), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[lexer_rule.CharStream, lexer_rule.StateAndResult]]([
            (
                lexer_rule.CharStream([
                    lexer_rule.Char('a'),
                    lexer_rule.Char('b'),
                ]),
                lexer_rule.StateAndResult(lexer_rule.CharStream([]), 'ab'),
            ),
            (
                lexer_rule.CharStream([
                    lexer_rule.Char('a'),
                    lexer_rule.Char('b'),
                    lexer_rule.Char('c'),
                ]),
                lexer_rule.StateAndResult(
                    lexer_rule.CharStream([
                        lexer_rule.Char('c'),
                    ]),
                    'ab'
                ),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    lexer_rule.And([
                        lexer_rule.Literal(lexer_rule.Char('a')),
                        lexer_rule.Literal(lexer_rule.Char('b')),
                    ]).apply(lexer_rule.Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[lexer_rule.CharStream]([
            lexer_rule.CharStream([]),
            lexer_rule.CharStream([lexer_rule.Char('b')]),
            lexer_rule.CharStream([
                lexer_rule.Char('a'),
                lexer_rule.Char('c'),
            ]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    lexer_rule.And([
                        lexer_rule.Literal(lexer_rule.Char('a')),
                        lexer_rule.Literal(lexer_rule.Char('b')),
                    ]).apply(lexer_rule.Scope({}), state)


class ZeroOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[lexer_rule.CharStream, lexer_rule.StateAndResult]]([
            (
                lexer_rule.CharStream([]),
                lexer_rule.StateAndResult(lexer_rule.CharStream([]), ''),
            ),
            (
                lexer_rule.CharStream([
                    lexer_rule.Char('a'),
                ]),
                lexer_rule.StateAndResult(lexer_rule.CharStream([]), 'a'),
            ),
            (
                lexer_rule.CharStream([
                    lexer_rule.Char('a'),
                    lexer_rule.Char('a'),
                ]),
                lexer_rule.StateAndResult(lexer_rule.CharStream([]), 'aa'),
            ),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    lexer_rule.ZeroOrMore(
                        lexer_rule.Literal(lexer_rule.Char('a')),
                    ).apply(lexer_rule.Scope({}), state),
                    expected_output
                )
