from typing import Optional, Tuple
import unittest
from core import lexer, parser
from . import builtins_, exprs, statements, vals


def _tok(value: str, rule_name: Optional[str] = None) -> lexer.Token:
    return lexer.Token(value, rule_name or value, lexer.Position(0, 0))


class ExprTest(unittest.TestCase):
    def test_eval(self):
        self.assertEqual(
            statements.Expr(
                exprs.literal(builtins_.int_(1))
            ).eval(vals.Scope({})),
            statements.Result()
        )

    def test_load(self):
        self.assertEqual(
            statements.Expr.load(
                statements.Statement.default_scope(),
                lexer.TokenStream([
                    _tok('1', 'int'),
                    _tok(';'),
                ])
            ),
            (
                lexer.TokenStream(),
                statements.Expr(
                    exprs.literal(builtins_.int_(1))
                )
            )
        )


class AssignmentTest(unittest.TestCase):
    def test_eval(self):
        scope = vals.Scope({})
        statements.Assignment(
            exprs.ref('a'),
            exprs.literal(builtins_.int_(1))
        ).eval(scope)
        self.assertEqual(scope['a'], builtins_.int_(1))

    def test_load(self):
        self.assertEqual(
            statements.Assignment.load(
                statements.Statement.default_scope(),
                lexer.TokenStream([
                    _tok('a', 'id'),
                    _tok('='),
                    _tok('1', 'int'),
                    _tok(';'),
                ])
            ),
            (
                lexer.TokenStream(),
                statements.Assignment(
                    exprs.ref('a'),
                    exprs.literal(builtins_.int_(1)),
                ),
            )
        )


class ReturnTest(unittest.TestCase):
    def test_eval(self):
        for return_, result in list[Tuple[statements.Return, statements.Result]]([
            (
                statements.Return(),
                statements.Result(
                    return_=statements.Result.Return(),
                )
            ),
            (
                statements.Return(exprs.literal(builtins_.int_(1))),
                statements.Result(
                    return_=statements.Result.Return(
                        builtins_.int_(1)
                    ),
                )
            ),
        ]):
            with self.subTest(return_=return_, result=result):
                self.assertEqual(
                    return_.eval(vals.Scope({})),
                    result
                )

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[statements.Return]]]([
            (
                lexer.TokenStream([
                    _tok('return'),
                    _tok(';'),
                ]),
                (lexer.TokenStream(), statements.Return()),
            ),
            (
                lexer.TokenStream([
                    _tok('return'),
                    _tok('1', 'int'),
                    _tok(';'),
                ]),
                (
                    lexer.TokenStream(),
                    statements.Return(
                        exprs.literal(builtins_.int_(1))
                    ),
                ),
            ),
            (
                lexer.TokenStream([
                    _tok('return'),
                    _tok('a', 'id'),
                    _tok(';'),
                ]),
                (
                    lexer.TokenStream(),
                    statements.Return(
                        exprs.ref('a')
                    ),
                ),
            ),
            (
                lexer.TokenStream([
                    _tok('return'),
                    _tok('a', 'id'),
                    _tok('+'),
                    _tok('b', 'id'),
                    _tok(';'),
                ]),
                (
                    lexer.TokenStream(),
                    statements.Return(
                        exprs.BinaryOperation(
                            exprs.BinaryOperation.Operator.ADD,
                            exprs.ref('a'),
                            exprs.ref('b'),
                        )
                    ),
                ),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    statements.Return.load(
                        statements.Statement.default_scope(),
                        state
                    ),
                    result
                )


class ClassTest(unittest.TestCase):
    def test_eval(self):
        scope = vals.Scope({})
        self.assertEqual(
            statements.Class(
                'c',
                statements.Block([
                    statements.Assignment(
                        exprs.ref('a'),
                        exprs.literal(builtins_.int_(1)),
                    ),
                ])
            ).eval(scope),
            statements.Result()
        )
        self.assertEqual(
            scope['c'],
            vals.Class(
                'c',
                vals.Scope({
                    'a': builtins_.int_(1),
                })
            )
        )

    def test_load(self):
        self.assertEqual(
            statements.Class.load(
                statements.Statement.default_scope(),
                lexer.TokenStream([
                    _tok('class'),
                    _tok('c', 'id'),
                    _tok('{'),
                    _tok('a', 'id'),
                    _tok('='),
                    _tok('1', 'int'),
                    _tok(';'),
                    _tok('}'),
                ])
            ),
            (
                lexer.TokenStream(),
                statements.Class(
                    'c',
                    statements.Block([
                        statements.Assignment(
                            exprs.ref('a'),
                            exprs.literal(builtins_.int_(1)),
                        ),
                    ])
                )
            )
        )


class NamespaceTest(unittest.TestCase):
    def test_eval(self):
        for namespace, expected_scope in list[Tuple[statements.Namespace, vals.Scope]]([
            (
                statements.Namespace(
                    statements.Block([
                        statements.Assignment(
                            exprs.ref('a'),
                            exprs.literal(builtins_.int_(1)),
                        ),
                    ])
                ),
                vals.Scope({
                })
            ),
            (
                statements.Namespace(
                    statements.Block([
                        statements.Assignment(
                            exprs.ref('a'),
                            exprs.literal(builtins_.int_(1)),
                        ),
                    ]),
                    _name='n'
                ),
                vals.Scope({
                    'n': vals.Namespace(
                        vals.Scope({
                            'a': builtins_.int_(1),
                        }),
                        name='n'
                    )
                })
            ),
        ]):
            with self.subTest(namespace=namespace, expected_scope=expected_scope):
                scope = vals.Scope({})
                self.assertEqual(
                    namespace.eval(scope),
                    statements.Result()
                )
                self.assertEqual(scope, expected_scope)

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[statements.Statement]]]([
            (
                lexer.TokenStream([
                    _tok('namespace'),
                    _tok('{'),
                    _tok('a', 'id'),
                    _tok('='),
                    _tok('1', 'int'),
                    _tok(';'),
                    _tok('}'),
                ]),
                (
                    lexer.TokenStream(),
                    statements.Namespace(
                        body=statements.Block([
                            statements.Assignment(
                                exprs.ref('a'),
                                exprs.literal(builtins_.int_(1)),
                            ),
                        ])
                    )
                ),
            ),
            (
                lexer.TokenStream([
                    _tok('namespace'),
                    _tok('n', 'id'),
                    _tok('{'),
                    _tok('a', 'id'),
                    _tok('='),
                    _tok('1', 'int'),
                    _tok(';'),
                    _tok('}'),
                ]),
                (
                    lexer.TokenStream(),
                    statements.Namespace(
                        _name='n',
                        body=statements.Block([
                            statements.Assignment(
                                exprs.ref('a'),
                                exprs.literal(builtins_.int_(1)),
                            ),
                        ])
                    )
                ),
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    statements.Namespace.load(
                        statements.Statement.default_scope(),
                        state,
                    ),
                    result
                )
