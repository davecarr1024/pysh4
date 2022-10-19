from typing import Tuple
import unittest
from . import builtins_, errors, vals, exprs
from core import lexer, parser


class ArgTest(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            exprs.Arg(exprs.literal(builtins_.int_(1))).eval(vals.Scope({})),
            vals.Arg(builtins_.int_(1))
        )

    def test_load(self):
        self.assertEqual(
            exprs.Arg.loader(
                parser.Scope[exprs.Expr]({
                    'expr': exprs.Expr.load,
                }),
            )(
                parser.Scope[exprs.Arg]({}),
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                ])
            ),
            (lexer.TokenStream(), exprs.Arg(exprs.literal(builtins_.int_(1)))),
        )


class ArgsTest(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            exprs.Args([
                exprs.Arg(exprs.literal(builtins_.int_(1))),
                exprs.Arg(exprs.literal(builtins_.int_(2))),
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
                        exprs.Arg(exprs.literal(builtins_.int_(1))),
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
                        exprs.Arg(exprs.literal(builtins_.int_(1))),
                        exprs.Arg(exprs.literal(builtins_.int_(2))),
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
                        exprs.Arg(exprs.literal(builtins_.int_(1))),
                        exprs.Arg(exprs.literal(builtins_.int_(2))),
                        exprs.Arg(exprs.literal(builtins_.int_(3))),
                    ])
                ),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    exprs.Args.load(
                        parser.Scope[exprs.Expr]({
                            'expr': exprs.Expr.load,
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
                            'expr': exprs.Expr.load,
                        }),
                        state
                    )


class RefTest(unittest.TestCase):
    def test_member_eval(self):
        self.assertEqual(
            exprs.Ref.Member('a').eval(
                vals.Scope({}),
                vals.Class(
                    'c',
                    vals.Scope({
                        'a': builtins_.int_(1),
                    })
                )
            ),
            builtins_.int_(1)
        )

    def test_member_load(self):
        self.assertEqual(
            exprs.Ref.Member.loader(
                parser.Scope[exprs.Expr]({}),
            )(
                parser.Scope[exprs.Ref.Tail]({}),
                lexer.TokenStream([
                    lexer.Token('.', '.', lexer.Position(0, 0)),
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                ])
            ),
            (lexer.TokenStream(), exprs.Ref.Member('a'))
        )

    def test_call_eval(self):
        self.assertEqual(
            exprs.Ref.Call(
                exprs.Args([])
            ).eval(vals.Scope({}), vals.Class('c', vals.Scope({}))),
            vals.Object(
                vals.Class('c', vals.Scope({})),
                vals.Scope({})
            )
        )

    def test_call_load(self):
        self.assertEqual(
            exprs.Ref.Call.loader(
                parser.Scope[exprs.Expr]({
                    'expr': exprs.Expr.load,
                }),
            )(
                parser.Scope[exprs.Ref.Tail]({}),
                lexer.TokenStream([
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token(',', ',', lexer.Position(0, 0)),
                    lexer.Token('2', 'int', lexer.Position(0, 0)),
                    lexer.Token(',', ',', lexer.Position(0, 0)),
                    lexer.Token('3', 'int', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ])
            ),
            (
                lexer.TokenStream(),
                exprs.Ref.Call(exprs.Args([
                    exprs.Arg(exprs.literal(builtins_.int_(1))),
                    exprs.Arg(exprs.literal(builtins_.int_(2))),
                    exprs.Arg(exprs.literal(builtins_.int_(3))),
                ])),
            )
        )

    def test_tail_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndMultipleResult[exprs.Ref.Tail]]]([
            (
                lexer.TokenStream(),
                (lexer.TokenStream(), []),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('.', '.', lexer.Position(0, 0)),
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                ]),
                (lexer.TokenStream(), [
                    exprs.Ref.Member('a'),
                ]),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (lexer.TokenStream(), [
                    exprs.Ref.Call(exprs.Args([])),
                ]),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('.', '.', lexer.Position(0, 0)),
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (lexer.TokenStream(), [
                    exprs.Ref.Member('a'),
                    exprs.Ref.Call(exprs.Args([])),
                ]),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    exprs.Ref.Tail.load(
                        parser.Scope[exprs.Expr]({
                            'expr': exprs.Expr.load,
                        }),
                        state
                    ),
                    result
                )

    def test_name_head_eval(self):
        self.assertEqual(
            exprs.Ref.Name('a').eval(vals.Scope({
                'a': builtins_.int_(1),
            })),
            builtins_.int_(1)
        )

    def test_name_head_load(self):
        self.assertEqual(
            exprs.Ref.Name.load(
                parser.Scope[exprs.Ref.Head]({}),
                lexer.TokenStream([
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                ])
            ),
            (lexer.TokenStream(), exprs.Ref.Name('a'))
        )

    def test_literal_head_eval(self):
        self.assertEqual(
            exprs.Ref.Literal(builtins_.int_(1)).eval(vals.Scope({})),
            builtins_.int_(1)
        )

    def test_literal_head_load(self):
        self.assertEqual(
            exprs.Ref.Literal.load(
                parser.Scope[exprs.Ref.Head]({}),
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                ])
            ),
            (lexer.TokenStream(), exprs.Ref.Literal(builtins_.int_(1)))
        )

    def test_head_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[exprs.Ref.Head]]]([
            (
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                ]),
                (lexer.TokenStream(), exprs.Ref.Literal(builtins_.int_(1)))
            ),
            (
                lexer.TokenStream([
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                ]),
                (lexer.TokenStream(), exprs.Ref.Name('a'))
            ),
        ]):
            with self.subTest(state=state, head=result):
                self.assertEqual(
                    exprs.Ref.Head.load(
                        parser.Scope[exprs.Ref.Head]({}),
                        state,
                    ),
                    result
                )

    def test_eval(self):
        for ref, result in list[Tuple[exprs.Ref, vals.Val]]([
            (
                exprs.Ref(exprs.Ref.Name('a')),
                builtins_.int_(1),
            ),
            (
                exprs.Ref(
                    exprs.Ref.Name('c'),
                    [
                        exprs.Ref.Member('a'),
                    ]
                ),
                builtins_.int_(2),
            ),
            (
                exprs.Ref(
                    exprs.Ref.Name('c'),
                    [
                        exprs.Ref.Call(exprs.Args([])),
                    ]
                ),
                vals.Object(
                    vals.Class('c', vals.Scope({'a': builtins_.int_(2)})),
                    vals.Scope({})
                )
            ),
        ]):
            with self.subTest(ref=ref, result=result):
                self.assertEqual(
                    ref.eval(vals.Scope({
                        'a': builtins_.int_(1),
                        'c': vals.Class(
                            'c',
                            vals.Scope({
                                'a': builtins_.int_(2),
                            })
                        ),
                    })),
                    result
                )

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[exprs.Ref]]]([
            (
                lexer.TokenStream([
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                ]),
                (lexer.TokenStream(), exprs.Ref(exprs.Ref.Name('a'))),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                    lexer.Token('.', '.', lexer.Position(0, 0)),
                    lexer.Token('b', 'id', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.Ref(
                        exprs.Ref.Name('a'),
                        [
                            exprs.Ref.Member('b'),
                        ]
                    )
                ),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token('b', 'id', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.Ref(
                        exprs.Ref.Name('a'),
                        [
                            exprs.Ref.Call(exprs.Args([
                                exprs.Arg(exprs.Ref(exprs.Ref.Name('b'))),
                            ])),
                        ]
                    )
                ),
            ),
            (
                lexer.TokenStream([
                    lexer.Token('a', 'id', lexer.Position(0, 0)),
                    lexer.Token('.', '.', lexer.Position(0, 0)),
                    lexer.Token('b', 'id', lexer.Position(0, 0)),
                    lexer.Token('(', '(', lexer.Position(0, 0)),
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token(')', ')', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.Ref(
                        exprs.Ref.Name('a'),
                        [
                            exprs.Ref.Member('b'),
                            exprs.Ref.Call(exprs.Args([
                                exprs.Arg(
                                    exprs.Ref(exprs.Ref.Literal(builtins_.int_(1)))),
                            ])),
                        ]
                    )
                ),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    exprs.Ref.load(
                        parser.Scope[exprs.Expr]({
                            'expr': exprs.Expr.load,
                        }),
                        state
                    ),
                    result
                )


class BinaryOperationTest(unittest.TestCase):
    def test_eval(self):
        for op, result in list[Tuple[exprs.BinaryOperation, vals.Val]]([
            (
                exprs.BinaryOperation(
                    exprs.BinaryOperation.Operator.ADD,
                    exprs.literal(builtins_.int_(1)),
                    exprs.literal(builtins_.int_(2)),
                ),
                builtins_.int_(3)
            ),
            (
                exprs.BinaryOperation(
                    exprs.BinaryOperation.Operator.SUB,
                    exprs.literal(builtins_.int_(1)),
                    exprs.literal(builtins_.int_(2)),
                ),
                builtins_.int_(-1)
            ),
            (
                exprs.BinaryOperation(
                    exprs.BinaryOperation.Operator.MUL,
                    exprs.literal(builtins_.int_(1)),
                    exprs.literal(builtins_.int_(2)),
                ),
                builtins_.int_(2)
            ),
            (
                exprs.BinaryOperation(
                    exprs.BinaryOperation.Operator.DIV,
                    exprs.literal(builtins_.int_(10)),
                    exprs.literal(builtins_.int_(2)),
                ),
                builtins_.int_(5)
            ),
            (
                exprs.BinaryOperation(
                    exprs.BinaryOperation.Operator.AND,
                    exprs.literal(builtins_.true),
                    exprs.literal(builtins_.false),
                ),
                builtins_.false
            ),
            (
                exprs.BinaryOperation(
                    exprs.BinaryOperation.Operator.OR,
                    exprs.literal(builtins_.true),
                    exprs.literal(builtins_.false),
                ),
                builtins_.true
            ),
        ]):
            with self.subTest(op=op, result=result):
                self.assertEqual(
                    op.eval(vals.Scope({})),
                    result
                )

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[exprs.Expr]]]([
            (
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token('+', '+', lexer.Position(0, 0)),
                    lexer.Token('2', 'int', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.BinaryOperation(
                        exprs.BinaryOperation.Operator.ADD,
                        exprs.literal(builtins_.int_(1)),
                        exprs.literal(builtins_.int_(2)),
                    )
                )
            ),
            (
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token('-', '-', lexer.Position(0, 0)),
                    lexer.Token('2', 'int', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.BinaryOperation(
                        exprs.BinaryOperation.Operator.SUB,
                        exprs.literal(builtins_.int_(1)),
                        exprs.literal(builtins_.int_(2)),
                    )
                )
            ),
            (
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token('*', '*', lexer.Position(0, 0)),
                    lexer.Token('2', 'int', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.BinaryOperation(
                        exprs.BinaryOperation.Operator.MUL,
                        exprs.literal(builtins_.int_(1)),
                        exprs.literal(builtins_.int_(2)),
                    )
                )
            ),
            (
                lexer.TokenStream([
                    lexer.Token('1', 'int', lexer.Position(0, 0)),
                    lexer.Token('/', '/', lexer.Position(0, 0)),
                    lexer.Token('2', 'int', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.BinaryOperation(
                        exprs.BinaryOperation.Operator.DIV,
                        exprs.literal(builtins_.int_(1)),
                        exprs.literal(builtins_.int_(2)),
                    )
                )
            ),
            (
                lexer.TokenStream([
                    lexer.Token('true', 'id', lexer.Position(0, 0)),
                    lexer.Token('and', 'and', lexer.Position(0, 0)),
                    lexer.Token('false', 'id', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.BinaryOperation(
                        exprs.BinaryOperation.Operator.AND,
                        exprs.ref('true'),
                        exprs.ref('false'),
                    )
                )
            ),
            (
                lexer.TokenStream([
                    lexer.Token('true', 'id', lexer.Position(0, 0)),
                    lexer.Token('or', 'or', lexer.Position(0, 0)),
                    lexer.Token('false', 'id', lexer.Position(0, 0)),
                ]),
                (
                    lexer.TokenStream(),
                    exprs.BinaryOperation(
                        exprs.BinaryOperation.Operator.OR,
                        exprs.ref('true'),
                        exprs.ref('false'),
                    )
                )
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    exprs.BinaryOperation.load(
                        exprs.Expr.default_scope(),
                        state
                    ),
                    result
                )
