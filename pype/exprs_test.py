from typing import Tuple
import unittest
from . import builtins_, errors, vals, exprs
from core import lexer, parser


class ArgTest(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            exprs.Arg(exprs.Literal(builtins_.int_(1))).eval(vals.Scope({})),
            vals.Arg(builtins_.int_(1))
        )

    def test_load(self):
        self.assertEqual(
            exprs.Arg.load(
                parser.Scope[exprs.Expr]({
                    'expr': exprs.Literal.load,
                }),
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                ])
            ),
            (lexer.TokenStream(), exprs.Arg(exprs.Literal(builtins_.int_(1)))),
        )


class ArgsTest(unittest.TestCase):
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

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, Tuple[lexer.TokenStream, exprs.Args]]]([
            (
                lexer.TokenStream([
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (lexer.TokenStream(), exprs.Args([])),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.Args([
                        exprs.Arg(exprs.Literal(builtins_.int_(1))),
                    ])
                ),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token(',', ',', lexer.Position(0, 0)),
                    lexer.Token('2', 'int', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.Args([
                        exprs.Arg(exprs.Literal(builtins_.int_(1))),
                        exprs.Arg(exprs.Literal(builtins_.int_(2))),
                    ])
                ),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token(',', ',', lexer.Position(0, 0)),
                    lexer.Token('2', 'int', lexer.Position(0, 0)),
                    lexer.Token(',', ',', lexer.Position(0, 0)),
                    lexer.Token('3', 'int', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.Args([
                        exprs.Arg(exprs.Literal(builtins_.int_(1))),
                        exprs.Arg(exprs.Literal(builtins_.int_(2))),
                        exprs.Arg(exprs.Literal(builtins_.int_(3))),
                    ])
                ),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    exprs.Args.load(
                        parser.Scope[exprs.Expr]({
                            'expr': exprs.Literal.load,
                        }),
                        state
                    ),
                    result
                )

    def test_load_fail(self):
        for state in list[lexer.TokenStream]([
            lexer.TokenStream([
                lexer.Token('(', '(', lexer.Position(0, 0)),
                lexer.Token('1', 'int', lexer.Position(0, 0)),
                lexer.Token(',', ',', lexer.Position(0, 0)),
                lexer.Token(')', ')', lexer.Position(0, 0)),
            ]),
            lexer.TokenStream([
                lexer.Token('(', '(', lexer.Position(0, 0)),
                lexer.Token('1', 'int', lexer.Position(0, 0)),
            ]),
            lexer.TokenStream([
                lexer.Token('(', '(', lexer.Position(0, 0)),
            ]),
        ]):
            with self.subTest(state):
                with self.assertRaises(errors.Error):
                    exprs.Args.load(
                        parser.Scope[exprs.Expr]({
                            'expr': exprs.Literal.load,
                        }),
                        state
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
