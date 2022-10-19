from typing import Tuple
import unittest
from . import builtins_, errors, params, vals


class ParamTest(unittest.TestCase):
    def test_bind(self):
        scope = vals.Scope({})
        params.Param('a').bind(scope, vals.Arg(builtins_.int_(1)))
        self.assertEqual(scope, vals.Scope({'a': builtins_.int_(1)}))


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
