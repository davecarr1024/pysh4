from typing import Sequence, Tuple
import unittest

from . import errors, stream

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
