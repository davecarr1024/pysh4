from typing import Sequence, Tuple
import unittest
from . import errors, processor

_State = Sequence[int]
_Result = int
_StateAndResult = processor.StateAndResult[_State, _Result]
_Rule = processor.Rule[_State, _Result]
_Scope = processor.Scope[_State, _Result]


def eq(value: int) -> _Rule:
    def rule(scope: _Scope, state: _State) -> _StateAndResult:
        if len(state) == 0:
            raise errors.Error(msg='empty state')
        if state[0] != value:
            raise errors.Error(msg=f'expected {value} got {state[0]}')
        return state[1:], value
    return rule


class EqTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1], ([], 1)),
            ([1, 2], ([2], 1)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    eq(1)(_Scope(), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    eq(1)(_Scope(), state)


class ScopeTest(unittest.TestCase):
    def test_getitem_fail(self):
        with self.assertRaises(errors.Error):
            _Scope({'a': eq(1)})['b']


class RefTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1], ([], 1)),
            ([1, 2], ([2], 1)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    processor.ref('a')(_Scope({'a': eq(1)}), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    processor.ref('a')(_Scope({'a': eq(1)}), state)
