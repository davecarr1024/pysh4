from dataclasses import dataclass, field
from typing import Callable, Generic, Iterator, Mapping, MutableSequence, Sequence, Tuple, TypeVar
from . import errors


_State = TypeVar('_State')
_Result = TypeVar('_Result')


StateAndResult = tuple[_State, _Result]

Rule = Callable[['Scope[_State, _Result]', _State],
                StateAndResult[_State, _Result]]


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


def ref(rule_name: str) -> Rule[_State, _Result]:
    def closure(scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        try:
            return scope[rule_name](scope, state)
        except errors.Error as error:
            raise errors.Error(rule_name=rule_name,
                               children=[error]) from error
    return closure


def or_(*rules: Rule[_State, _Result]) -> Rule[_State, _Result]:
    def closure(scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        rule_errors: MutableSequence[errors.Error] = []
        for rule in rules:
            try:
                return rule(scope, state)
            except errors.Error as error:
                rule_errors.append(error)
        raise errors.Error(children=rule_errors)
    return closure


ResultCombiner = Callable[[Sequence[_Result]], _Result]


def and_(
    rules: Sequence[Rule[_State, _Result]],
    result_combiner: ResultCombiner[_Result],
) -> Rule[_State, _Result]:
    def closure(scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        results: MutableSequence[_Result] = []
        for rule in rules:
            state, result = rule(scope, state)
            results.append(result)
        return state, result_combiner(results)
    return closure


def zero_or_more(
    rule: Rule[_State, _Result],
    result_combiner: ResultCombiner[_Result],
) -> Rule[_State, _Result]:
    def closure(scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        results: MutableSequence[_Result] = []
        while True:
            try:
                state, result = rule(scope, state)
                results.append(result)
            except errors.Error:
                return state, result_combiner(results)
    return closure


def one_or_more(
    rule: Rule[_State, _Result],
    result_combiner: ResultCombiner[_Result],
) -> Rule[_State, _Result]:
    def closure(scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        state, result = rule(scope, state)
        results: MutableSequence[_Result] = [result]
        while True:
            try:
                state, result = rule(scope, state)
                results.append(result)
            except errors.Error:
                return state, result_combiner(results)
    return closure


def zero_or_one(
    rule: Rule[_State, _Result],
    result_combiner: ResultCombiner[_Result],
) -> Rule[_State, _Result]:
    def closure(scope: Scope[_State, _Result], state: _State) -> StateAndResult[_State, _Result]:
        try:
            return rule(scope, state)
        except errors.Error:
            return state, result_combiner([])
    return closure
