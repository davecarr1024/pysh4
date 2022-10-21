from typing import Tuple
import unittest
from . import pype, vals, builtins_


class PypeTest(unittest.TestCase):
    def test_eval(self):
        for input, result in list[Tuple[str, vals.Val]]([
            ('1;', builtins_.int_(1)),
            ('3 - 2;', builtins_.int_(1)),
            ('a = 1; a;', builtins_.int_(1)),
            ('a = 3 - 2; a;', builtins_.int_(1)),
            (
                r'''
                namespace n {
                    a = 1;
                }
                n.a;
                ''',
                builtins_.int_(1),
            ),
            (
                r'''
                def f(a) {
                    return a;
                }
                f(1);
                ''',
                builtins_.int_(1),
            ),
            (
                r'''
                class c {
                    a = 1;
                }
                c.a;
                ''',
                builtins_.int_(1),
            ),
            (
                r'''
                class c {
                    def __init__(self) {
                        self.a = 1;
                    }
                }
                c().a;
                ''',
                builtins_.int_(1),
            ),
        ]):
            with self.subTest(input=input, result=result):
                self.assertEqual(pype.eval(input), result)
