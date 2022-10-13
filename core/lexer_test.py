from typing import Tuple
import unittest
from . import lexer, regex


_Literal = regex.Literal[lexer.Char]
_OneOrMore = regex.OneOrMore[lexer.Char]


class LexerTest(unittest.TestCase):
    def test_apply(self):
        for lexer_, input, expected_result in list[Tuple[lexer.Rule, str, lexer.TokenStream]]([
            (
                lexer.Lexer(
                    r=_Literal('a'),
                ),
                'a',
                lexer.TokenStream([
                    lexer.Token('a', 'r', lexer.Position(0, 0)),
                ]),
            ),
            (
                lexer.Lexer(
                    r=_OneOrMore(_Literal('a')),
                    s=_OneOrMore(_Literal('b')),
                ),
                'aaaabbbaab',
                lexer.TokenStream([
                    lexer.Token('aaaa', 'r', lexer.Position(0, 0)),
                    lexer.Token('bbb', 's', lexer.Position(0, 4)),
                    lexer.Token('aa', 'r', lexer.Position(0, 7)),
                    lexer.Token('b', 's', lexer.Position(0, 9)),
                ]),
            ),
        ]):
            with self.subTest(lexer_=lexer_, input=input, expected_result=expected_result):
                state, actual_result = lexer_(
                    lexer.Scope({}), lexer.load_char_stream(input))
                self.assertEqual(len(state), 0)
                self.assertEqual(actual_result, expected_result)


class CharStreamTest(unittest.TestCase):
    def test_load(self):
        for input, output in list[Tuple[str, lexer.CharStream]]([
            (
                '',
                lexer.CharStream(),
            ),
            (
                'abc',
                lexer.CharStream([
                    lexer.Char('a', lexer.Position(0, 0)),
                    lexer.Char('b', lexer.Position(0, 1)),
                    lexer.Char('c', lexer.Position(0, 2)),
                ]),
            ),
            (
                'abc\ndef',
                lexer.CharStream([
                    lexer.Char('a', lexer.Position(0, 0)),
                    lexer.Char('b', lexer.Position(0, 1)),
                    lexer.Char('c', lexer.Position(0, 2)),
                    lexer.Char('\n', lexer.Position(0, 3)),
                    lexer.Char('d', lexer.Position(1, 0)),
                    lexer.Char('e', lexer.Position(1, 1)),
                    lexer.Char('f', lexer.Position(1, 2)),
                ]),
            ),
        ]):
            with self.subTest(input=input, output=output):
                self.assertEqual(lexer.load_char_stream(input), output)
