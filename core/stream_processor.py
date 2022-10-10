from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, MutableSequence, Sequence, Sized, TypeVar, final
from . import processor, errors

_Item_co = TypeVar('_Item_co', covariant=True)
_Result = TypeVar('_Result')


@dataclass(frozen=True)
@final
class Stream(Generic[_Item_co], Iterable[_Item_co], Sized):
    _items: Sequence[_Item_co]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[_Item_co]:
        return iter(self._items)

    def __add__(self, rhs: 'Stream[_Item_co]') -> 'Stream[_Item_co]':
        return Stream[_Item_co](list(self._items) + list(rhs._items))

    @property
    def empty(self) -> bool:
        return len(self._items) == 0

    @property
    def head(self) -> _Item_co:
        if self.empty:
            raise errors.Error(msg='empty stream')
        return self._items[0]

    @property
    def tail(self) -> 'Stream[_Item_co]':
        if self.empty:
            raise errors.Error(msg='empty stream')
        return Stream[_Item_co](self._items[1:])


StateError = processor.StateError[Stream[_Item_co]]
RuleError = processor.RuleError[Stream[_Item_co], _Result]
RuleNameError = processor.RuleNameError
StateAndResult = processor.StateAndResult[Stream[_Item_co], _Result]
Rule = processor.Rule[Stream[_Item_co], _Result]
Scope = processor.Scope[Stream[_Item_co], _Result]
Processor = processor.Processor[Stream[_Item_co], _Result]
UnaryRule = processor.UnaryRule[Stream[_Item_co], _Result]
NaryRule = processor.NaryRule[Stream[_Item_co], _Result]
ResultCombiner = processor.ResultCombiner[_Result]
Ref = processor.Ref[Stream[_Item_co], _Result]
Or = processor.Or[Stream[_Item_co], _Result]
And = processor.And[Stream[_Item_co], _Result]
ZeroOrMore = processor.ZeroOrMore[Stream[_Item_co], _Result]
OneOrMore = processor.OneOrMore[Stream[_Item_co], _Result]
ZeroOrOne = processor.ZeroOrOne[Stream[_Item_co], _Result]

_Item = TypeVar('_Item')


class HeadRule(Rule[_Item, _Result], ABC):
    @abstractmethod
    def result(self, head: _Item) -> _Result:
        ...

    def validate(self, head: _Item) -> None:
        ...

    def apply(self, scope: Scope[_Item, _Result], state: Stream[_Item]) -> StateAndResult[_Item, _Result]:
        if state.empty:
            raise errors.Error(msg='empty stream')
        self.validate(state.head)
        return StateAndResult[_Item, _Result](state.tail, self.result(state.head))


class UntilEmpty(UnaryRule[_Item_co, _Result], ResultCombiner[_Result]):
    def apply(self, scope: Scope[_Item_co, _Result], state: Stream[_Item_co]) -> StateAndResult[_Item_co, _Result]:
        results: MutableSequence[_Result] = []
        while not state.empty:
            try:
                child_state_and_result = self.child.apply(scope, state)
            except errors.Error as error:
                raise RuleError[_Item_co, _Result](
                    rule=self, state=state, children=[error]) from error
            state = child_state_and_result.state
            results.append(child_state_and_result.result)
        return StateAndResult[_Item_co, _Result](state, self.combine_results(results))
