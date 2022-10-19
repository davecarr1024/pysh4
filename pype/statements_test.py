from typing import Optional
import unittest
from core import lexer, parser
from . import builtins_, exprs, errors, statements, vals


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
