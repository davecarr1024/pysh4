from dataclasses import dataclass, field
import unittest
from . import builtins_, errors, vals, funcs, func, statements, params, exprs

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    # pylint: disable=protected-access
    __import__(
        'sys').modules['unittest.util']._MAX_LENGTH = 999999999
    # pylint: enable=protected-access

_int = builtins_.int_


@dataclass(frozen=True)
class _BindableVal(vals.Val):
    @property
    def can_bind(self) -> bool:
        return True

    def bind(self, object_: vals.Val) -> vals.Val:
        return _BoundVal(object_)


@dataclass(frozen=True)
class _BoundVal(vals.Val):
    value: vals.Val = field(compare=False, repr=False)


def arg(value: int) -> vals.Arg:
    return vals.Arg(_int(value))


def args(*values: int) -> vals.Args:
    return vals.Args([arg(value) for value in values])


class ArgsTest(unittest.TestCase):
    def test_prepend(self):
        self.assertEqual(
            args(1).prepend(arg(2)),
            args(2, 1)
        )


class ScopeTest(unittest.TestCase):
    def test_contains(self):
        self.assertIn('a', vals.Scope({'a': _int(1)}))
        self.assertNotIn('b', vals.Scope({'a': _int(1)}))
        self.assertIn('a', vals.Scope({}, parent=vals.Scope({'a': _int(1)})))

    def test_getitem(self):
        self.assertEqual(
            vals.Scope({'a': _int(1)})['a'],
            _int(1)
        )
        self.assertEqual(
            vals.Scope({}, parent=vals.Scope({'a': _int(1)}))['a'],
            _int(1)
        )
        with self.assertRaises(errors.Error):
            vals.Scope({})['a']

    def test_setitem(self):
        s = vals.Scope({})
        s['a'] = _int(1)
        self.assertEqual(s['a'], _int(1))

    def test_all_vals(self):
        self.assertDictEqual(
            vals.Scope({'a': _int(1)}, parent=vals.Scope(
                {'a': _int(2), 'b': _int(3)})).all_vals,
            {'a': _int(1), 'b': _int(3)}
        )

    def test_bind_vals(self):
        self.assertDictEqual(
            vals.Scope({
                'a': _int(1),
                'b': _BindableVal(),
            }).bind_vals(_int(2)),
            {
                'b': _BoundVal(_int(2))
            }
        )


class ClassTest(unittest.TestCase):
    def test_instantiate(self):
        c = vals.Class(
            'c',
            vals.Scope({
                'a': _int(1),
                'b': _BindableVal(),
            }),
        )
        self.assertEqual(
            c.instantiate(),
            vals.Object(
                c,
                vals.Scope({
                    'b': _BoundVal(builtins_.none),
                }, parent=vals.Scope({
                    'a': _int(1),
                })),
            )
        )

    def test_init(self):
        c = vals.Class(
            'c',
            vals.Scope({
                '__init__': funcs.BindableFunc(
                    func.Func(
                        '__init__',
                        params.Params([params.Param('self')]),
                        statements.Block([
                            statements.Assignment(
                                exprs.Ref(
                                    exprs.Ref.Name('self'),
                                    [exprs.Ref.Member('a')]
                                ),
                                exprs.literal(builtins_.int_(1)),
                            ),
                        ])
                    )
                ),
            })
        )
        o = c(vals.Scope({}), vals.Args([]))
        self.assertEqual(o['a'], builtins_.int_(1))
