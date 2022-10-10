from typing import Sequence, Tuple
import unittest

from . import errors, lexer, regex


class RegexTest(unittest.TestCase):
    def test_apply(self):
        self.assertEqual(
            lexer.Regex('r', regex.Literal('a')).apply(
                lexer.Scope({}),
                lexer.CharStream([lexer.Char('a', lexer.Position(0, 0))])),
            lexer.StateAndResult(
                lexer.CharStream([]),
                lexer.TokenStream([
                    lexer.Token('r', 'a', lexer.Position(0, 0)),
                ])
            )
        )

    def test_apply_fail(self):
        with self.assertRaises(errors.Error):
            lexer.Regex(
                'r',
                regex.Literal('a'),
            ).apply(
                lexer.Scope({}),
                lexer.CharStream([]),
            )


class LexerTest(unittest.TestCase):
    def test_load_char_stream(self):
        for input_str, expected_result in list[Tuple[str, lexer.CharStream]]([
            ('', lexer.CharStream([])),
            (
                'a\nb',
                lexer.CharStream([
                    lexer.Char('a', lexer.Position(0, 0)),
                    lexer.Char('\n', lexer.Position(0, 1)),
                    lexer.Char('b', lexer.Position(1, 0)),
                ])
            ),
        ]):
            with self.subTest(input_str=input_str, expected_result=expected_result):
                self.assertEqual(
                    lexer.load_char_stream(input_str),
                    expected_result
                )

    def test_ctor_fail(self):
        for rules in list[Sequence[lexer.Regex]]([
            [
                lexer.Regex('_lexer_a', regex.Literal('a')),
            ],
            [
                lexer.Regex('a', regex.Literal('a')),
                lexer.Regex('a', regex.Literal('b')),
            ],
        ]):
            with self.subTest(rules=rules):
                with self.assertRaises(errors.Error):
                    lexer.Lexer(rules)

    def test_apply(self):
        for lexer_, input_str, expected_result in list[Tuple[lexer.Lexer, str, lexer.StateAndResult]]([
            (
                lexer.Lexer([]),
                '',
                lexer.StateAndResult(
                    lexer.CharStream([]),
                    lexer.TokenStream([]),
                ),
            ),
            (
                lexer.Lexer([
                    lexer.Regex('a', regex.Literal('a')),
                ]),
                'aaa',
                lexer.StateAndResult(
                    lexer.CharStream([]),
                    lexer.TokenStream([
                        lexer.Token('a', 'a', lexer.Position(0, 0)),
                        lexer.Token('a', 'a', lexer.Position(0, 1)),
                        lexer.Token('a', 'a', lexer.Position(0, 2)),
                    ]),
                ),
            ),
        ]):
            with self.subTest(lexer_=lexer_, input_str=input_str, expected_result=expected_result):
                self.assertEqual(
                    lexer_.apply_state(lexer.load_char_stream(input_str)),
                    expected_result
                )
