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


class ResultCombiner(processor.ResultCombiner[_Result]):
    def combine_results(self, results: Sequence[_Result]) -> _Result:
        return sum(results)


_Ref = processor.Ref[_State, _Result]
_Or = processor.Or[_State, _Result]


class _And(processor.And[_State, _Result], ResultCombiner):
    ...


class _ZeroOrMore(processor.ZeroOrMore[_State, _Result], ResultCombiner):
    ...


class _OneOrMore(processor.OneOrMore[_State, _Result], ResultCombiner):
    ...


class _ZeroOrOne(processor.ZeroOrOne[_State, _Result], ResultCombiner):
    ...


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
                    _Ref('a')(_Scope({'a': eq(1)}), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Ref('a')(_Scope({'a': eq(1)}), state)


class OrTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1], ([], 1)),
            ([2], ([], 2)),
            ([1, 3], ([3], 1)),
            ([2, 3], ([3], 2)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    _Or([eq(1), eq(2)])(_Scope(), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [3],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Or([eq(1), eq(2)])(_Scope(), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1, 2], ([], 3)),
            ([1, 2, 3], ([3], 3)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    _And([eq(1), eq(2)])(_Scope(), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [1],
            [2],
            [1, 3],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _And([eq(1), eq(2)])(_Scope(), state)


class ZeroOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([], ([], 0)),
            ([1], ([], 1)),
            ([1, 1], ([], 2)),
            ([2], ([2], 0)),
            ([1, 2], ([2], 1)),
            ([1, 1, 2], ([2], 2)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    _ZeroOrMore(eq(1))(_Scope(), state),
                    output
                )


class OneOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1], ([], 1)),
            ([1, 1], ([], 2)),
            ([1, 2], ([2], 1)),
            ([1, 1, 2], ([2], 2)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    _OneOrMore(eq(1))(_Scope(), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            ([], ([], 0)),
            ([2], ([2], 0)),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _OneOrMore(eq(1))(_Scope(), state)


class ZeroOrOneTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([], ([], 0)),
            ([1], ([], 1)),
            ([2], ([2], 0)),
            ([1, 2], ([2], 1)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    _ZeroOrOne(eq(1))(_Scope(), state),
                    output
                )
