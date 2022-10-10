from dataclasses import dataclass
from typing import Sequence, Tuple
import unittest
from . import errors, processor

_State = Sequence[int]
_Result = int
_StateAndResult = processor.StateAndResult[_State, _Result]
_Rule = processor.Rule[_State, _Result]
_Scope = processor.Scope[_State, _Result]
_Processor = processor.Processor[_State, _Result]
_Ref = processor.Ref[_State, _Result]
_Or = processor.Or[_State, _Result]


class _ResultCombiner(processor.ResultCombiner[_Result]):
    def combine_results(self, results: Sequence[_Result]) -> _Result:
        return sum(results)


class _And(processor.And[_State, _Result], _ResultCombiner):
    ...


class _ZeroOrMore(processor.ZeroOrMore[_State, _Result], _ResultCombiner):
    ...


class _OneOrMore(processor.OneOrMore[_State, _Result], _ResultCombiner):
    ...


class _ZeroOrOne(processor.ZeroOrOne[_State, _Result], _ResultCombiner):
    ...


@dataclass(frozen=True)
class _Eq(_Rule):
    value: int

    def apply(self, scope: _Scope, state: _State) -> _StateAndResult:
        if len(state) == 0:
            raise errors.Error(msg='empty state')
        if state[0] != self.value:
            raise errors.Error(msg=f'state {state[0]} != value {self.value}')
        return _StateAndResult(state[1:], state[0])


class EqTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_State, _StateAndResult]]([
            ([1], _StateAndResult([], 1)),
            ([1, 2], _StateAndResult([2], 1)),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _Eq(1).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Eq(1).apply(_Scope({}), state)


class ScopeTest(unittest.TestCase):
    def test_apply_rule(self):
        self.assertEqual(
            _Scope({
                'a': _Eq(1),
            }).apply_rule('a', [1]),
            _StateAndResult([], 1)
        )


class ProcessorTest(unittest.TestCase):
    def test_apply_state(self):
        self.assertEqual(
            _Processor({'a': _Eq(1)}, 'a').apply_state([1]),
            _StateAndResult([], 1)
        )


class RefTest(unittest.TestCase):
    def test_apply(self):
        self.assertEqual(
            _Ref('a').apply(_Scope({'a': _Eq(1)}), [1]),
            _StateAndResult([], 1)
        )

    def test_apply_fail(self):
        with self.assertRaises(errors.Error):
            _Ref('a').apply(_Scope({}), [1])


class OrTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_State, _StateAndResult]]([
            ([1], _StateAndResult([], 1)),
            ([2], _StateAndResult([], 2)),
            ([1, 3], _StateAndResult([3], 1)),
            ([2, 3], _StateAndResult([3], 2)),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _Or([_Eq(1), _Eq(2)]).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [3],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Or([_Eq(1), _Eq(2)]).apply(_Scope({}), state)


class AndTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_State, _StateAndResult]]([
            ([1, 2], _StateAndResult([], 3)),
            ([1, 2, 3], _StateAndResult([3], 3)),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _And([_Eq(1), _Eq(2)]).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
            [1, 1],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _And([_Eq(1), _Eq(2)]).apply(_Scope({}), state)


class ZeroOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_State, _StateAndResult]]([
            ([], _StateAndResult([], 0)),
            ([1], _StateAndResult([], 1)),
            ([1, 1], _StateAndResult([], 2)),
            ([2], _StateAndResult([2], 0)),
            ([1, 2], _StateAndResult([2], 1)),
            ([1, 1, 2], _StateAndResult([2], 2)),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _ZeroOrMore(_Eq(1)).apply(_Scope({}), state),
                    expected_output
                )


class OneOrMoreTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_State, _StateAndResult]]([
            ([1], _StateAndResult([], 1)),
            ([1, 1], _StateAndResult([], 2)),
            ([1, 2], _StateAndResult([2], 1)),
            ([1, 1, 2], _StateAndResult([2], 2)),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _OneOrMore(_Eq(1)).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            [],
            [2],
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _OneOrMore(_Eq(1)).apply(_Scope({}), state)


class ZeroOrOneTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_State, _StateAndResult]]([
            ([], _StateAndResult([], 0)),
            ([1], _StateAndResult([], 1)),
            ([2], _StateAndResult([2], 0)),
            ([1, 2], _StateAndResult([2], 1)),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _ZeroOrOne(_Eq(1)).apply(_Scope({}), state),
                    expected_output
                )
