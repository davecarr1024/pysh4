from typing import Optional, Tuple
import unittest
from core import lexer, parser
from . import builtins_, errors, params, vals


def _tok(value: str, rule_name: Optional[str] = None) -> lexer.Token:
    return lexer.Token(value, rule_name or value, lexer.Position(0, 0))


class ParamTest(unittest.TestCase):
    def test_bind(self):
        scope = vals.Scope({})
        params.Param('a').bind(scope, vals.Arg(builtins_.int_(1)))
        self.assertEqual(scope, vals.Scope({'a': builtins_.int_(1)}))

    def test_load(self):
        self.assertEqual(
            params.Param.load(
                lexer.TokenStream([
                    _tok('a', 'id'),
                ])
            ),
            (lexer.TokenStream(), params.Param('a'))
        )


class ParamsTest(unittest.TestCase):
    def test_tail(self):
        for params_, tail in list[Tuple[params.Params, params.Params]]([
            (
                params.Params([params.Param('a')]),
                params.Params([]),
            ),
            (
                params.Params([params.Param('a'), params.Param('b')]),
                params.Params([params.Param('b')]),
            ),
        ]):
            with self.subTest(params_=params_, tail=tail):
                self.assertEqual(params_.tail, tail)

    def test_tail_fail(self):
        with self.assertRaises(errors.Error):
            _ = params.Params([]).tail

    def test_bind(self):
        self.assertEqual(
            params.Params([
                params.Param('a'),
                params.Param('b'),
            ]).bind(
                vals.Scope({
                    'a': builtins_.int_(1),
                }),
                vals.Args([
                    vals.Arg(builtins_.int_(2)),
                    vals.Arg(builtins_.int_(3)),
                ])
            ),
            vals.Scope({
                'a': builtins_.int_(2),
                'b': builtins_.int_(3),
            })
        )

    def test_bind_fail(self):
        with self.assertRaises(errors.Error):
            params.Params([params.Param('a')]).bind(
                vals.Scope({}), vals.Args([]))

    def test_load(self):
        for state, result in list[Tuple[lexer.TokenStream, parser.StateAndResult[params.Params]]]([
            (
                lexer.TokenStream([
                    _tok('('),
                    _tok(')'),
                ]),
                (
                    lexer.TokenStream(),
                    params.Params([]),
                )
            ),
            (
                lexer.TokenStream([
                    _tok('('),
                    _tok('a', 'id'),
                    _tok(')'),
                ]),
                (
                    lexer.TokenStream(),
                    params.Params([
                        params.Param('a'),
                    ]),
                )
            ),
            (
                lexer.TokenStream([
                    _tok('('),
                    _tok('a', 'id'),
                    _tok(','),
                    _tok('b', 'id'),
                    _tok(')'),
                ]),
                (
                    lexer.TokenStream(),
                    params.Params([
                        params.Param('a'),
                        params.Param('b'),
                    ]),
                )
            ),
        ]):
            with self.subTest(state=state, result=result):
                self.assertEqual(
                    params.Params.load(state),
                    result
                )
