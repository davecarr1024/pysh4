from typing import Sequence, Tuple
import unittest

from . import errors, processor, stream

_Item = int
_Stream = stream.Stream[_Item]


class StreamTest(unittest.TestCase):
    def test_add(self):
        for lhs, rhs, output in list[Tuple[_Stream, _Stream, _Stream]]([
            (
                _Stream(),
                _Stream(),
                _Stream(),
            ),
            (
                _Stream([1]),
                _Stream(),
                _Stream([1]),
            ),
            (
                _Stream(),
                _Stream([1]),
                _Stream([1]),
            ),
            (
                _Stream([1]),
                _Stream([2]),
                _Stream([1, 2]),
            ),
        ]):
            with self.subTest(lhs=lhs, rhs=rhs, output=output):
                self.assertEqual(
                    lhs + rhs,
                    output
                )

    def test_len(self):
        for stream, output in list[Tuple[_Stream, int]]([
            (_Stream(), 0),
            (_Stream([1]), 1),
            (_Stream([1, 2]), 2),
        ]):
            with self.subTest(stream=stream, output=output):
                self.assertEqual(len(stream), output)

    def test_empty(self):
        for stream, output in list[Tuple[_Stream, bool]]([
            (_Stream(), True),
            (_Stream([1]), False),
        ]):
            with self.subTest(stream=stream, output=output):
                self.assertEqual(stream.empty, output)

    def test_head(self):
        for stream, output in list[Tuple[_Stream, int]]([
            (_Stream([1]), 1),
            (_Stream([1, 2]), 1),
        ]):
            with self.subTest(stream=stream, output=output):
                self.assertEqual(stream.head, output)

    def test_head_fail(self):
        with self.assertRaises(errors.Error):
            _ = _Stream([]).head

    def test_tail(self):
        for stream, output in list[Tuple[_Stream, _Stream]]([
            (_Stream([1]), _Stream()),
            (_Stream([1, 2]), _Stream([2])),
        ]):
            with self.subTest(stream=stream, output=output):
                self.assertEqual(stream.tail, output)

    def test_tail_fail(self):
        with self.assertRaises(errors.Error):
            _ = _Stream([]).tail

    def test_concat(self):
        for streams, output in list[Tuple[Sequence[_Stream], _Stream]]([
            ([], _Stream()),
            ([_Stream()], _Stream()),
            ([_Stream([1])], _Stream([1])),
            ([_Stream([1]), _Stream([2])], _Stream([1, 2])),
        ]):
            with self.subTest(streams=streams, output=output):
                self.assertEqual(
                    _Stream.concat(streams),
                    output
                )


_State = _Stream
_Result = int
_StateAndResult = processor.StateAndResult[_State, _Result]
_Rule = processor.Rule[_State, _Result]
_Scope = processor.Scope[_State, _Result]


def eq(value: int) -> _Rule:
    def result(head: int) -> _Result:
        if head != value:
            raise errors.Error(msg=f'expected {value} got {head}')
        return head
    return stream.head_rule(result)


result_combiner: processor.ResultCombiner[_Result] = sum


class UntilEmptyTest(unittest.TestCase):
    def test_apply(self):
        for state, output in list[Tuple[_State, _StateAndResult]]([
            (
                _Stream(),
                (_Stream([]), 0),
            ),
            (
                _Stream([1]),
                (_Stream([]), 1),
            ),
            (
                _Stream([1, 1]),
                (_Stream([]), 2),
            ),
        ]):
            with self.subTest(state=state, output=output):
                self.assertEqual(
                    stream.until_empty(
                        eq(1),
                        result_combiner
                    )(_Scope(), state),
                    output
                )

    def test_apply_fail(self):
        for state in list[_State]([
            _Stream([2]),
            _Stream([1, 2]),
        ]):
            with self.subTest(state=state):
                with self.assertRaises(errors.Error):
                    stream.until_empty(eq(1), result_combiner)(_Scope(), state)
