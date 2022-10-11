from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, Iterator, MutableSequence, Sequence, Sized, TypeVar

from . import errors, processor

_Item = TypeVar('_Item', covariant=True)


@dataclass(frozen=True)
class Stream(Generic[_Item], Iterable[_Item], Sized):
    _items: Sequence[_Item] = field(default_factory=list[_Item])

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[_Item]:
        return iter(self._items)

    def __add__(self, rhs: 'Stream[_Item]') -> 'Stream[_Item]':
        return Stream[_Item](list(self._items)+list(rhs._items))

    @property
    def empty(self) -> bool:
        return len(self) == 0

    @property
    def head(self) -> _Item:
        if self.empty:
            raise errors.Error(msg='empty stream')
        return self._items[0]

    @property
    def tail(self) -> 'Stream[_Item]':
        if self.empty:
            raise errors.Error(msg='empty stream')
        return Stream[_Item](self._items[1:])

    @staticmethod
    def concat(streams: Sequence['Stream[_Item]']) -> 'Stream[_Item]':
        return sum(streams, Stream[_Item]([]))


_Result = TypeVar('_Result')


def until_empty(
    rule: processor.Rule[Stream[_Item], _Result],
    result_combiner: processor.ResultCombiner[_Result],
) -> processor.Rule[Stream[_Item], _Result]:
    def closure(
        scope: processor.Scope[Stream[_Item], _Result],
        state: Stream[_Item],
    ) -> processor.StateAndResult[Stream[_Item], _Result]:
        results: MutableSequence[_Result] = []
        while not state.empty:
            state, result = rule(scope, state)
            results.append(result)
        return state, result_combiner(results)
    return closure


def head_rule(result_func: Callable[[_Item], _Result]) -> processor.Rule[Stream[_Item], _Result]:
    def closure(
        scope: processor.Scope[Stream[_Item], _Result],
        state: Stream[_Item],
    ) -> processor.StateAndResult[Stream[_Item], _Result]:
        return state.tail, result_func(state.head)
    return closure
