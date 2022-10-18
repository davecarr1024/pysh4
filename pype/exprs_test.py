from typing import Tuple
import unittest
from . import builtins_, errors, vals, exprs
from core import lexer, parser


class Arg(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            exprs.Arg(exprs.Literal(builtins_.int_(1))).eval(vals.Scope({})),
            vals.Arg(builtins_.int_(1))
        )


class Args(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            exprs.Args([
                exprs.Arg(exprs.Literal(builtins_.int_(1))),
                exprs.Arg(exprs.Literal(builtins_.int_(2))),
            ]).eval(vals.Scope({})),
            vals.Args([
                vals.Arg(builtins_.int_(1)),
                vals.Arg(builtins_.int_(2)),
            ])
        )


class Ref(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            exprs.Ref('a').eval(vals.Scope({'a': builtins_.int_(1)})),
            builtins_.int_(1)
        )

    def test_eval_fail(self):
        with self.assertRaises(errors.Error):
            exprs.Ref('a').eval(vals.Scope({}))

    def test_load(self):
        self.assertEqual(
            exprs.Ref.load(
                parser.Scope[exprs.Expr]({}),
                lexer.TokenStream(
                    [lexer.Token('a', 'id', lexer.Position(0, 0))]),
            ),
            (lexer.TokenStream([]), exprs.Ref('a'))
        )


class LiteralTest(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            exprs.Literal(builtins_.int_(1)).eval(vals.Scope({})),
            builtins_.int_(1)
        )

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[exprs.Expr]]]([
            (
                lexer.TokenStream(
                    [lexer.Token('1', 'int', lexer.Position(0, 0))]),
                (lexer.TokenStream(), exprs.Literal(builtins_.int_(1)))
            ),
            (
                lexer.TokenStream(
                    [lexer.Token('3.14', 'float', lexer.Position(0, 0))]),
                (lexer.TokenStream(), exprs.Literal(builtins_.float_(3.14)))
            ),
            (
                lexer.TokenStream(
                    [lexer.Token('"abc"', 'str', lexer.Position(0, 0))]),
                (lexer.TokenStream(), exprs.Literal(builtins_.str_('abc')))
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    exprs.Literal.load(parser.Scope[exprs.Expr]({}), state),
                    result
                )
