from typing import Optional, Tuple
import unittest
from core import lexer, parser
from . import func, errors, params, builtins_, statements, vals, exprs


def _tok(value: str, rule_name: Optional[str] = None) -> lexer.Token:
    return lexer.Token(value, rule_name or value, lexer.Position(0, 0))


class FuncTest(unittest.TestCase):
    def test_call(self):
        for func_, args, result in list[Tuple[func.Func, vals.Args, vals.Val]]([
            (
                func.Func(
                    'f',
                    params.Params([]),
                    statements.Block([
                        statements.Return(
                            exprs.literal(builtins_.int_(1)),
                        ),
                    ])
                ),
                vals.Args([]),
                builtins_.int_(1),
            ),
            (
                func.Func(
                    'f',
                    params.Params([
                        params.Param('a'),
                    ]),
                    statements.Block([
                        statements.Return(
                            exprs.ref('a'),
                        ),
                    ])
                ),
                vals.Args([vals.Arg(builtins_.int_(1))]),
                builtins_.int_(1),
            ),
            (
                func.Func(
                    'f',
                    params.Params([
                        params.Param('a'),
                    ]),
                    statements.Block([
                        statements.Return(
                            exprs.ref('a'),
                        ),
                        statements.Return(
                            exprs.literal(builtins_.int_(2)),
                        ),
                    ])
                ),
                vals.Args([vals.Arg(builtins_.int_(1))]),
                builtins_.int_(1),
            ),
        ]):
            with self.subTest(func_=func_, args=args, result=result):
                self.assertEqual(
                    func_(vals.Scope({}), args),
                    result
                )

    def test_call_fail(self):
        for func_, args in list[Tuple[func.Func, vals.Args]]([
            (
                func.Func(
                    'f',
                    params.Params([params.Param('a')]),
                    statements.Block([]),
                ),
                vals.Args([]),
            ),
        ]):
            with self.subTest(func_=func_, args=args):
                with self.assertRaises(errors.Error):
                    func_(vals.Scope({}), args)

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[statements.Statement]]]([
            (
                lexer.TokenStream([
                    _tok('def'),
                    _tok('f', 'id'),
                    _tok('('),
                    _tok(')'),
                    _tok('{'),
                    _tok('}'),
                ]),
                (
                    lexer.TokenStream(),
                    func.Decl(
                        'f',
                        params.Params([]),
                        statements.Block([]),
                    )
                )
            ),
            (
                lexer.TokenStream([
                    _tok('def'),
                    _tok('f', 'id'),
                    _tok('('),
                    _tok('a', 'id'),
                    _tok(','),
                    _tok('b', 'id'),
                    _tok(')'),
                    _tok('{'),
                    _tok('return'),
                    _tok('a', 'id'),
                    _tok('+'),
                    _tok('b', 'id'),
                    _tok(';'),
                    _tok('}'),
                ]),
                (
                    lexer.TokenStream(),
                    func.Decl(
                        'f',
                        params.Params([
                            params.Param('a'),
                            params.Param('b'),
                        ]),
                        statements.Block([
                            statements.Return(
                                exprs.BinaryOperation(
                                    exprs.BinaryOperation.Operator.ADD,
                                    exprs.ref('a'),
                                    exprs.ref('b'),
                                )
                            ),
                        ]),
                    )
                )
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    func.Decl.load(
                        statements.Statement.default_scope(),
                        state,
                    ),
                    result
                )
