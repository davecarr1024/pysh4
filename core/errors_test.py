import unittest
from . import errors


class ErrorTest(unittest.TestCase):
    def test_with_rule_name(self):
        self.assertEqual(
            errors.Error(msg='a', children=[
                         errors.Error(msg='b')]).with_rule_name('r'),
            errors.Error(msg='a', rule_name='r',
                         children=[errors.Error(msg='b')])
        )
