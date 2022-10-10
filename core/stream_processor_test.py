from dataclasses import dataclass
from typing import Sequence, Tuple
import unittest
from . import errors, stream_processor

_Item = int
_Result = int
_Stream = stream_processor.Stream[_Item]
_StateAndResult = stream_processor.StateAndResult[_Item, _Result]
_Scope = stream_processor.Scope[_Item, _Result]
_HeadRule = stream_processor.HeadRule[_Item, _Result]


@dataclass(frozen=True)
class _Eq(_HeadRule):
    value: int

    def result(self, head: int) -> int:
        if head != self.value:
            raise errors.Error(msg=f'head {head} != value {self.value}')
        return head


class _ResultCombiner(stream_processor.ResultCombiner[_Result]):
    def combine_results(self, results: Sequence[_Result]) -> _Result:
        return sum(results)


class _UntilEmpty(stream_processor.UntilEmpty[_Item, _Result], _ResultCombiner):
    ...


class StreamTest(unittest.TestCase):
    def test_empty(self):
        self.assertTrue(_Stream([]).empty)
        self.assertFalse(_Stream([1]).empty)

    def test_head(self):
        self.assertEqual(_Stream([1, 2]).head, 1)

    def test_head_fail(self):
        with self.assertRaises(errors.Error):
            _ = _Stream([]).head

    def test_tail(self):
        self.assertEqual(_Stream([1, 2]).tail, _Stream([2]))

    def test_tail_fail(self):
        with self.assertRaises(errors.Error):
            _ = _Stream([]).tail

    def test_add(self):
        self.assertEqual(
            _Stream([1]) + _Stream([2]),
            _Stream([1, 2])
        )


class EqTest(unittest.TestCase):
    def test_apply(self):
        self.assertEqual(
            _Eq(1).apply(_Scope({}), _Stream([1])),
            _StateAndResult(_Stream([]), 1)
        )

    def test_apply_fail(self):
        for state in list[_Stream]([
            _Stream([]),
            _Stream([2]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _Eq(1).apply(_Scope({}), state)


class UntilEmptyTest(unittest.TestCase):
    def test_apply(self):
        for state, expected_output in list[Tuple[_Stream, _StateAndResult]]([
            (_Stream([]), _StateAndResult(_Stream([]), 0)),
            (_Stream([1]), _StateAndResult(_Stream([]), 1)),
            (_Stream([1, 1]), _StateAndResult(_Stream([]), 2)),
        ]):
            with self.subTest(state=state, expected_output=expected_output):
                self.assertEqual(
                    _UntilEmpty(_Eq(1)).apply(_Scope({}), state),
                    expected_output
                )

    def test_apply_fail(self):
        for state in list[_Stream]([
            _Stream([2]),
            _Stream([1, 2]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    _UntilEmpty(_Eq(1)).apply(_Scope({}), state)
