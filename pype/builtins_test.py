import unittest
from . import builtins_, vals


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

    def test_lt_true(self):
        self.assertEqual(
            builtins_.int_(1)['__lt__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.int_(2))])
            ),
            builtins_.true
        )

    def test_lt_false(self):
        self.assertEqual(
            builtins_.int_(2)['__lt__'](
                vals.Scope({}),
                vals.Args([vals.Arg(builtins_.int_(1))])
            ),
            builtins_.false
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


class NoneTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(builtins_.none, builtins_.none)
