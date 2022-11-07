import unittest
from . import vals


class ClassTest(unittest.TestCase):
    def test_instantiate(self):
        c = vals.Class(
            'c',
            vals.Scope()
        )
        self.assertEqual(
            c.instantiate(),
            vals.Object(
                c,
                vals.Scope()
            )
        )
