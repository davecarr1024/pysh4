from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Sequence, Sized, TypeVar, final
from . import processor, errors

_Item = TypeVar('_Item')
_Result = TypeVar('_Result')


@dataclass(frozen=True)
@final
class Stream(Generic[_Item], Iterable[_Item], Sized):
    _items: Sequence[_Item]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[_Item]:
        return iter(self._items)

    @property
    def empty(self) -> bool:
        return len(self._items) == 0

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


StateAndResult = processor.StateAndResult[Stream[_Item], _Result]
Rule = processor.Rule[Stream[_Item], _Result]
Scope = processor.Scope[Stream[_Item], _Result]
Processor = processor.Processor[Stream[_Item], _Result]
Ref = processor.Ref[Stream[_Item], _Result]
Or = processor.Or[Stream[_Item], _Result]


class HeadRule(Rule[_Item, _Result], ABC):
    @abstractmethod
    def result(self, head: _Item) -> _Result:
        ...

    def apply(self, scope: Scope[_Item, _Result], state: Stream[_Item]) -> StateAndResult[_Item, _Result]:
        if state.empty:
            raise errors.Error(msg='empty stream')
        return StateAndResult[_Item, _Result](state.tail, self.result(state.head))
