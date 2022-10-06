from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Iterator, Mapping, MutableSequence, Sequence, TypeVar
from . import errors

_State = TypeVar('_State')
_Result = TypeVar('_Result')


@dataclass(frozen=True)
class StateAndResult(Generic[_State, _Result]):
    state: _State
    result: _Result


class Rule(Generic[_State, _Result], ABC):
    @abstractmethod
    def apply(self, scope: 'Scope[_State, _Result]', state: _State) -> StateAndResult[_State, _Result]:
        ...


@dataclass(frozen=True)
class Scope(Generic[_State, _Result], Mapping[str, Rule[_State, _Result]]):
    _rules: Mapping[str, Rule[_State, _Result]]

    def __len__(self) -> int:
        return len(self._rules)

    def __iter__(self) -> Iterator[str]:
        return iter(self._rules)

    def __getitem__(self, rule_name: str) -> Rule[_State, _Result]:
        if rule_name not in self._rules:
            raise errors.Error(msg=f'unknown rule {rule_name}')
        return self._rules[rule_name]

    def apply_rule(self, rule_name: str, state: _State) -> StateAndResult[_State, _Result]:
        try:
            return self[rule_name].apply(self, state)
        except errors.Error as error:
            raise error.with_rule_name(rule_name) from error


@dataclass(frozen=True)
class Processor(Scope[_State, _Result], Rule[_State, _Result]):
    root: str

    def apply_state(self, state: _State) -> StateAndResult[_State, _Result]:
        return self.apply(self, state)

    def apply(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        return scope.apply_rule(self.root, state)


@dataclass(frozen=True)
class NaryRule(Rule[_State, _Result]):
    children: Sequence[Rule[_State, _Result]]


@dataclass(frozen=True)
class UnaryRule(Rule[_State, _Result]):
    child: Rule[_State, _Result]


class ResultCombiner(Generic[_Result]):
    @abstractmethod
    def combine_results(self, results: Sequence[_Result]) -> _Result:
        ...


@dataclass(frozen=True)
class Ref(Rule[_State, _Result]):
    name: str

    def apply(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        return scope[self.name].apply(scope, state)


class Or(NaryRule[_State, _Result]):
    def apply(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        child_errors: MutableSequence[errors.Error] = []
        for child in self.children:
            try:
                return child.apply(scope, state)
            except errors.Error as error:
                child_errors.append(error)
        raise errors.Error(children=child_errors)


class And(NaryRule[_State, _Result], ResultCombiner[_Result]):
    def apply(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        results: MutableSequence[_Result] = []
        for child in self.children:
            try:
                child_state_and_result = child.apply(scope, state)
            except errors.Error as error:
                raise error.as_child() from error
            state = child_state_and_result.state
            results.append(child_state_and_result.result)
        return StateAndResult(state, self.combine_results(results))


class ZeroOrMore(UnaryRule[_State, _Result], ResultCombiner[_Result]):
    def apply(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        results: MutableSequence[_Result] = []
        while True:
            try:
                child_state_and_result = self.child.apply(scope, state)
                state = child_state_and_result.state
                results.append(child_state_and_result.result)
            except errors.Error:
                return StateAndResult(state, self.combine_results(results))


class OneOrMore(UnaryRule[_State, _Result], ResultCombiner[_Result]):
    def apply(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        try:
            child_state_and_result = self.child.apply(scope, state)
        except errors.Error as error:
            raise error.as_child() from error
        state = child_state_and_result.state
        results: MutableSequence[_Result] = [child_state_and_result.result]
        while True:
            try:
                child_state_and_result = self.child.apply(scope, state)
                state = child_state_and_result.state
                results.append(child_state_and_result.result)
            except errors.Error:
                return StateAndResult(state, self.combine_results(results))


class ZeroOrOne(UnaryRule[_State, _Result], ResultCombiner[_Result]):
    def apply(self, scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        try:
            child_state_and_result = self.child.apply(scope, state)
            state = child_state_and_result.state
            results = [child_state_and_result.result]
        except errors.Error:
            results = []
        return StateAndResult(state, self.combine_results(results))
