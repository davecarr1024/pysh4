from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Iterable, Iterator, MutableSequence, Sequence, Sized, TypeVar

from . import errors, processor

_Item = TypeVar('_Item', covariant=True)


class Emptyable(ABC):
    @property
    @abstractmethod
    def empty(self) -> bool:
        ...


@dataclass(frozen=True, repr=False)
class Stream(Generic[_Item], Iterable[_Item], Sized, Emptyable):
    _items: Sequence[_Item] = field(default_factory=list[_Item])

    def __repr__(self) -> str:
        return repr(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[_Item]:
        return iter(self._items)

    def __add__(self, rhs: 'Stream[_Item]') -> 'Stream[_Item]':
        return self.__class__(list(self._items)+list(rhs._items))

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
        return self.__class__(self._items[1:])

    @classmethod
    def concat(cls, streams: Sequence['Stream[_Item]']) -> 'Stream[_Item]':
        return sum(streams, cls())


_State = TypeVar('_State', bound=Emptyable)
_Result = TypeVar('_Result')


class UntilEmpty(processor.UnaryMultipleResultRule[_State, _Result]):
    def __repr__(self) -> str:
        return f'{self.rule}!'

    def __call__(self, scope: processor.Scope[_State, _Result], state: _State) -> processor.StateAndMultipleResult[_State, _Result]:
        results: MutableSequence[_Result] = []
        while not state.empty:
            state, result = self.rule(scope, state)
            results.append(result)
        return state, results
