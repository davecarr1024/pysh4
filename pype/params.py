from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence, Sized
from . import errors, vals


@dataclass(frozen=True, repr=False)
class Param:
    name: str

    def __repr__(self) -> str:
        return self.name

    def bind(self, scope: vals.Scope, arg: vals.Arg) -> None:
        scope[self.name] = arg.value


@dataclass(frozen=True, repr=False)
class Params(Iterable[Param], Sized):
    _params: Sequence[Param]

    def __repr__(self) -> str:
        return f'({", ".join(str(param) for param in self._params)})'

    def __len__(self) -> int:
        return len(self._params)

    def __iter__(self) -> Iterator[Param]:
        return iter(self._params)

    @property
    def tail(self) -> 'Params':
        if len(self._params) == 0:
            raise errors.Error(msg='empty params')
        return Params(self._params[1:])

    def bind(self, scope: vals.Scope, args: vals.Args) -> vals.Scope:
        '''bind the given args in a new child scope'''
        if len(self) != len(args):
            raise errors.Error(
                msg=f'param count mismatch: expected {len(self)} but got {len(args)}')
        scope = scope.as_child()
        for param, arg in zip(self, args):
            param.bind(scope, arg)
        return scope
