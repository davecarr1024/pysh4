from collections import OrderedDict
from typing import Tuple
import unittest
from . import errors, lexer, regex


class LexerTest(unittest.TestCase):
    def test_apply(self):
        for lexer_, input, expected_result in list[Tuple[lexer.Rule, str, lexer.TokenStream]]([
            (
                lexer.lexer(
                    r=regex.literal('a'),
                ),
                'a',
                lexer.TokenStream([
                    lexer.Token('a', 'r', lexer.Position(0, 0)),
                ]),
            ),
            (
                lexer.lexer(
                    r=regex.one_or_more(regex.literal('a')),
                    s=regex.one_or_more(regex.literal('b')),
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
                    lexer.Scope(), lexer.load_char_stream(input))
                self.assertEqual(len(state), 0)
                self.assertEqual(actual_result, expected_result)
