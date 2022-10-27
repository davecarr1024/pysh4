from typing import Tuple
import unittest
from . import builtins_, errors, vals


class IntTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(builtins_.int_(1), builtins_.int_(1))
        self.assertNotEqual(builtins_.int_(1), builtins_.int_(2))

    def test_class(self):
        self.assertEqual(
            builtins_.int_(1).class_,
            builtins_.IntClass
        )

    def test_add(self):
        self.assertEqual(
            builtins_.int_(1)['__add__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.int_(2))])
            ),
            builtins_.int_(3)
        )

    def test_sub(self):
        self.assertEqual(
            builtins_.int_(1)['__sub__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.int_(2))])
            ),
            builtins_.int_(-1)
        )

    def test_mul(self):
        self.assertEqual(
            builtins_.int_(1)['__mul__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.int_(2))])
            ),
            builtins_.int_(2)
        )

    def test_div(self):
        self.assertEqual(
            builtins_.int_(10)['__div__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.int_(2))])
            ),
            builtins_.int_(5)
        )

    def test_comps(self):
        for lhs, rhs, func, result in list[Tuple[int, int, str, bool]]([
            (1, 2, '__lt__', True),
            (2, 1, '__lt__', False),
            (1, 1, '__le__', True),
            (2, 1, '__le__', False),
            (2, 1, '__gt__', True),
            (1, 2, '__gt__', False),
            (1, 1, '__ge__', True),
            (1, 2, '__ge__', False),
            (1, 1, '__eq__', True),
            (1, 2, '__eq__', False),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs, func=func, result=result):
                self.assertEqual(
                    builtins_.int_(lhs)[func](
                        vals.Scope({}),
                        vals.Args([vals.Arg(builtins_.int_(rhs))])
                    ),
                    builtins_.bool_(result)
                )

    def test_intify(self):
        self.assertEqual(
            builtins_.IntObject.from_val(vals.Scope({}), builtins_.int_(1)),
            1
        )

    def test_intify_fail(self):
        with self.assertRaises(errors.Error):
            builtins_.IntObject.from_val(vals.Scope({}), builtins_.str_(''))

    def test_bool(self):
        for val, result in list[Tuple[int, bool]]([
            (1, True),
            (0, False),
        ]):
            with self.subTest(val=val, result=result):
                self.assertEqual(
                    builtins_.int_(val)['__bool__'](
                        vals.Scope({}), vals.Args([])),
                    builtins_.bool_(result)
                )


class FloatTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(builtins_.float_(1.1), builtins_.float_(1.1))
        self.assertNotEqual(builtins_.float_(1.1), builtins_.float_(1.2))

    def test_class(self):
        self.assertEqual(
            builtins_.float_(1.1).class_,
            builtins_.FloatClass
        )

    def test_add(self):
        self.assertEqual(
            builtins_.float_(1.1)['__add__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.float_(1.2))])
            ),
            builtins_.float_(2.3)
        )

    def test_sub(self):
        self.assertEqual(
            builtins_.float_(1.1)['__sub__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.float_(1.2))])
            ),
            builtins_.float_(-.1)
        )

    def test_mul(self):
        self.assertEqual(
            builtins_.float_(1.1)['__mul__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.float_(1.2))])
            ),
            builtins_.float_(1.32)
        )

    def test_div(self):
        self.assertEqual(
            builtins_.float_(1.1)['__div__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.float_(2.))])
            ),
            builtins_.float_(0.55)
        )

    def test_comps(self):
        for lhs, rhs, func, result in list[Tuple[float, float, str, bool]]([
            (1.1, 1.2, '__lt__', True),
            (1.2, 1.1, '__lt__', False),
            (1.1, 1.1, '__le__', True),
            (1.2, 1.1, '__le__', False),
            (1.2, 1.1, '__gt__', True),
            (1.1, 1.2, '__gt__', False),
            (1.1, 1.1, '__ge__', True),
            (1.1, 1.2, '__ge__', False),
            (1.1, 1.1, '__eq__', True),
            (1.1, 1.2, '__eq__', False),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs, func=func, result=result):
                self.assertEqual(
                    builtins_.float_(lhs)[func](
                        vals.Scope({}),
                        vals.Args([vals.Arg(builtins_.float_(rhs))])
                    ),
                    builtins_.bool_(result)
                )

    def test_floatify(self):
        self.assertEqual(
            builtins_.FloatObject.from_val(
                vals.Scope({}), builtins_.float_(1.1)),
            1.1
        )

    def test_floatify_fail(self):
        with self.assertRaises(errors.Error):
            builtins_.FloatObject.from_val(vals.Scope({}), builtins_.str_(''))

    def test_bool(self):
        for val, result in list[Tuple[float, bool]]([
            (1.1, True),
            (0, False),
        ]):
            with self.subTest(val=val, result=result):
                self.assertEqual(
                    builtins_.float_(val)['__bool__'](
                        vals.Scope({}), vals.Args([])),
                    builtins_.bool_(result)
                )


class StrTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(builtins_.str_('a'), builtins_.str_('a'))
        self.assertNotEqual(builtins_.str_('a'), builtins_.str_('b'))

    def test_class(self):
        self.assertEqual(
            builtins_.str_('a').class_,
            builtins_.StrClass
        )

    def test_add(self):
        self.assertEqual(
            builtins_.str_('a')['__add__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.str_('b'))])
            ),
            builtins_.str_('ab')
        )

    def test_strify(self):
        self.assertEqual(
            builtins_.StrObject.from_val(vals.Scope({}), builtins_.str_('a')),
            'a'
        )

    def test_strify_fail(self):
        with self.assertRaises(errors.Error):
            builtins_.StrObject.from_val(vals.Scope({}), builtins_.false)

    def test_bool(self):
        for val, result in list[Tuple[str, bool]]([
            ('a', True),
            ('', False),
        ]):
            with self.subTest(val=val, result=result):
                self.assertEqual(
                    builtins_.str_(val)['__bool__'](
                        vals.Scope({}), vals.Args([])),
                    builtins_.bool_(result)
                )


class BoolTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(builtins_.bool_(True), builtins_.bool_(True))
        self.assertEqual(builtins_.bool_(True), builtins_.true)
        self.assertEqual(builtins_.bool_(False), builtins_.bool_(False))
        self.assertEqual(builtins_.bool_(False), builtins_.false)
        self.assertNotEqual(builtins_.bool_(True), builtins_.bool_(False))
        self.assertEqual(builtins_.true, builtins_.true)
        self.assertEqual(builtins_.false, builtins_.false)

    def test_class(self):
        self.assertEqual(
            builtins_.true.class_,
            builtins_.BoolClass
        )

    def test_and(self):
        self.assertEqual(
            builtins_.true['__and__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.false)])
            ),
            builtins_.false
        )

    def test_or(self):
        self.assertEqual(
            builtins_.true['__or__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.false)])
            ),
            builtins_.true
        )

    def test_from_val(self):
        for val, result in list[Tuple[vals.Val, bool]]([
            (builtins_.true, True),
            (builtins_.false, False),
            (builtins_.int_(1), True),
            (builtins_.int_(0), False),
            (builtins_.float_(0.1), True),
            (builtins_.float_(0), False),
            (builtins_.str_('a'), True),
            (builtins_.str_(''), False),
        ]):
            with self.subTest(val=val, result=result):
                self.assertEqual(
                    builtins_.BoolObject.from_val(vals.Scope({}), val),
                    result
                )


class NoneTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(builtins_.none, builtins_.none)
