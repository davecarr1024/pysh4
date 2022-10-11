from typing import Tuple
import unittest
from . import errors, processor, regex

_Char = regex.Char
_CharStream = regex.CharStream[_Char]
_Rule = regex.Rule[_Char]
_Scope = regex.Scope[_Char]
_StateAndResult = regex.StateAndResult[_Char]


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
