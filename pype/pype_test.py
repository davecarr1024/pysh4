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
            (
                r'''
                class c {
                    def __init__(self) {
                        self.a = 2;
                    }
                }
                o = c();
                o.a = 1;
                o.a;
                ''',
                builtins_.int_(1),
            ),
            (
                r'''
                class c {
                    def __init__(self) {
                        self.a = 2;
                    }
                    def get(self) {
                        return self.a / 2;
                    }
                }
                c().get();
                ''',
                builtins_.int_(1),
            ),
            (
                r'''
                class c {
                    def __init__(self) {
                        self.a = 0;
                    }
                    def set(self, a) {
                        self.a = a;
                    }
                    def get(self) {
                        return self.a;
                    }
                }
                o = c();
                o.set(1);
                o.get();
                ''',
                builtins_.int_(1),
            ),
        ]):
            with self.subTest(input=input, result=result):
                self.assertEqual(pype.eval(input), result)
