from dataclasses import dataclass
from typing import Sequence, Tuple
import unittest
from . import errors, processor

_State = Sequence[int]
_Result = int
_StateAndResult = processor.StateAndResult[_State, _Result]
_StateAndMultipleResult = processor.StateAndMultipleResult[_State, _Result]
_StateAndOptionalResult = processor.StateAndOptionalResult[_State, _Result]
_Rule = processor.Rule[_State, _Result]
_Scope = processor.Scope[_State, _Result]


@dataclass(frozen=True)
class Eq:
    value: int

    def __call__(self, scope: _Scope, state: _State) -> _StateAndResult:
        if len(state) == 0:
            raise errors.Error(msg='empty state')
        if state[0] != self.value:
            raise errors.Error(msg=f'expected {self.value} got {state[0]}')
        return state[1:], state[0]


@dataclass(frozen=True)
class _ResultCombiner(processor.MultipleResultCombiner[_State, _Result]):
    def __call__(self, scope: _Scope, state: _State) -> _StateAndResult:
        state, results = self.rule(scope, state)
        return state, sum(results)


_Ref = processor.Ref[_State, _Result]
_Or = processor.Or[_State, _Result]


class EqTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1], ([], 1)),
            ([1, 2], ([2], 1)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    Eq(1)(_Scope({}), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    Eq(1)(_Scope({}), state)


class ScopeTest(unittest.TestCase):
    def test_getitem_fail(self):
        with self.assertRaises(errors.Error):
            _Scope({'a': Eq(1)})['b']

    def test_or(self):
        self.assertEqual(
            _Scope({
                'a': Eq(1),
                'b': Eq(2),
            }) | _Scope({
                'b': Eq(3),
                'c': Eq(4),
            }),
            _Scope({
                'a': Eq(1),
                'b': Eq(3),
                'c': Eq(4),
            })
        )


class RefTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1], ([], 1)),
            ([1, 2], ([2], 1)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    _Ref('a')(_Scope({'a': Eq(1)}), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Ref('a')(_Scope({'a': Eq(1)}), state)


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
                    _Or([Eq(1), Eq(2)])(_Scope({}), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [3],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Or([Eq(1), Eq(2)])(_Scope({}), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndMultipleResult]]([
            ([1, 2], ([], [1, 2])),
            ([1, 2, 3], ([3], [1, 2])),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    processor.And[_State, _Result](
                        [Eq(1), Eq(2)])(_Scope({}), state),
                    output
                )

    def test_apply_single_result(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            ([1, 2], ([], 3)),
            ([1, 2, 3], ([3], 3)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    _ResultCombiner(
                        processor.And[_State, _Result](
                            [Eq(1), Eq(2)]
                        )
                    )(_Scope({}), state),
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
                    processor.And[_State, _Result](
                        [Eq(1), Eq(2)])(_Scope({}), state)


class ZeroOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndMultipleResult]]([
            ([], ([], [])),
            ([1], ([], [1])),
            ([1, 1], ([], [1, 1])),
            ([2], ([2], [])),
            ([1, 2], ([2], [1])),
            ([1, 1, 2], ([2], [1, 1])),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    processor.ZeroOrMore[_State, _Result](
                        Eq(1))(_Scope({}), state),
                    output
                )


class OneOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndMultipleResult]]([
            ([1], ([], [1])),
            ([1, 1], ([], [1, 1])),
            ([1, 2], ([2], [1])),
            ([1, 1, 2], ([2], [1, 1])),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    processor.OneOrMore[_State, _Result](
                        Eq(1))(_Scope({}), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    processor.OneOrMore[_State, _Result](
                        Eq(1))(_Scope({}), state)


class ZeroOrOneTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndOptionalResult]]([
            ([], ([], None)),
            ([1], ([], 1)),
            ([2], ([2], None)),
            ([1, 2], ([2], 1)),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    processor.ZeroOrOne[_State, _Result](
                        Eq(1))(_Scope({}), state),
                    output
                )
