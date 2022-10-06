from dataclasses import dataclass
from typing import Sequence
import unittest
from . import errors, processor

_State = Sequence[int]
_Result = int
_StateAndResult = processor.StateAndResult[_State, _Result]
_Rule = processor.Rule[_State, _Result]
_Scope = processor.Scope[_State, _Result]
_Processor = processor.Processor[_State, _Result]
_Ref = processor.Ref[_State, _Result]


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
        self.assertEqual(
            _Eq(1).apply(_Scope({}), [1]),
            _StateAndResult([], 1)
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
