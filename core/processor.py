from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, Iterator, Mapping, MutableSequence, Sequence, Sized, Tuple, TypeVar
from . import errors


_State = TypeVar('_State')
_Result = TypeVar('_Result')


StateAndResult = tuple[_State, _Result]

Rule = Callable[['Scope[_State, _Result]', _State],
                StateAndResult[_State, _Result]]


@dataclass(frozen=True, kw_only=True)
class StateError(errors.NaryError, Generic[_State]):
    state: _State


@dataclass(frozen=True, kw_only=True)
class RuleError(StateError, Generic[_State, _Result]):
    rule: Rule[_State, _Result]


@dataclass(frozen=True, kw_only=True)
class RuleNameError(errors.UnaryError):
    rule_name: str


@dataclass(frozen=True)
class Scope(Generic[_State, _Result], Mapping[str, Rule[_State, _Result]]):
    _rules: Mapping[str, Rule[_State, _Result]] = field(
        default_factory=dict[str, Rule[_State, _Result]])

    def __getitem__(self, name: str) -> Rule[_State, _Result]:
        if name not in self._rules:
            raise errors.Error(msg=f'unknown rule {name}')
        return self._rules[name]

    def __len__(self) -> int:
        return len(self._rules)

    def __iter__(self) -> Iterator[str]:
        return iter(self._rules)


@dataclass(frozen=True)
class Ref(Generic[_State, _Result]):
    rule_name: str

    def __call__(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        try:
            return scope[self.rule_name](scope, state)
        except errors.Error as error:
            raise RuleNameError(rule_name=self.rule_name,
                                child=error) from error


@dataclass(frozen=True)
class NaryRule(Generic[_State, _Result], Iterable[Rule[_State, _Result]], Sized):
    rules: Sequence[Rule[_State, _Result]]

    def __len__(self) -> int:
        return len(self.rules)

    def __iter__(self) -> Iterator[Rule[_State, _Result]]:
        return iter(self.rules)


@dataclass(frozen=True, repr=False)
class Or(NaryRule[_State, _Result]):
    def __repr__(self):
        return f'({"|".join(repr(rule) for rule in self.rules)})'

    def __call__(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        rule_errors: MutableSequence[errors.Error] = []
        for rule in self.rules:
            try:
                return rule(scope, state)
            except errors.Error as error:
                rule_errors.append(error)
        raise RuleError(rule=self, state=state, children=rule_errors)


class ResultCombiner(Generic[_Result], ABC):
    @abstractmethod
    def combine_results(self, results: Sequence[_Result]) -> _Result:
        ...


class And(NaryRule[_State, _Result], ResultCombiner[_Result]):
    def __repr__(self) -> str:
        return f'({" ".join(repr(rule) for rule in self.rules)})'

    def __call__(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        results: MutableSequence[_Result] = []
        for rule in self.rules:
            state, result = rule(scope, state)
            results.append(result)
        return state, self.combine_results(results)


@dataclass(frozen=True)
class UnaryRule(Generic[_State, _Result]):
    rule: Rule[_State, _Result]


class ZeroOrMore(UnaryRule[_State, _Result], ResultCombiner):
    def __repr__(self) -> str:
        return f'{self.rule}*'

    def __call__(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        results: MutableSequence[_Result] = []
        while True:
            try:
                state, result = self.rule(scope, state)
                results.append(result)
            except errors.Error:
                return state, self.combine_results(results)


class OneOrMore(UnaryRule[_State, _Result], ResultCombiner):
    def __repr__(self) -> str:
        return f'{self.rule}+'

    def __call__(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        state, result = self.rule(scope, state)
        results: MutableSequence[_Result] = [result]
        while True:
            try:
                state, result = self.rule(scope, state)
                results.append(result)
            except errors.Error:
                return state, self.combine_results(results)


class ZeroOrOne(UnaryRule[_State, _Result], ResultCombiner):
    def __repr__(self) -> str:
        return f'{self.rule}?'

    def __call__(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        try:
            return self.rule(scope, state)
        except errors.Error:
            return state, self.combine_results([])
