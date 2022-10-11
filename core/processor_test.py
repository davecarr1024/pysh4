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


result_combiner: processor.ResultCombiner[_Result] = sum


def and_(*rules: _Rule) -> _Rule:
    return processor.and_(rules, result_combiner)


def zero_or_more(rule: _Rule) -> _Rule:
    return processor.zero_or_more(rule, result_combiner)


def one_or_more(rule: _Rule) -> _Rule:
    return processor.one_or_more(rule, result_combiner)


def zero_or_one(rule: _Rule) -> _Rule:
    return processor.zero_or_one(rule, result_combiner)


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
                    processor.or_(eq(1), eq(2))(_Scope(), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [3],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    processor.or_(eq(1), eq(2))(_Scope(), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1, 2], ([], 3)),
            ([1, 2, 3], ([3], 3)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    and_(eq(1), eq(2))(_Scope(), state),
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
                    and_(eq(1), eq(2))(_Scope(), state)


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
                    zero_or_more(eq(1))(_Scope(), state),
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
                    one_or_more(eq(1))(_Scope(), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            ([], ([], 0)),
            ([2], ([2], 0)),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    one_or_more(eq(1))(_Scope(), state)


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
                    zero_or_one(eq(1))(_Scope(), state),
                    output
                )
