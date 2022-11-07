from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Sequence, Sized
from . import errors, scope


class Type(ABC):
    def __str__(self) -> str:
        return self.name

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    def members(self) -> 'Scope':
        return Scope()

    @property
    def signatures(self) -> 'Signatures':
        return Signatures()

    def check_assignable(self, rhs: 'Type') -> None:
        if self != rhs:
            raise errors.Error(
                msg=f'type {rhs} cannot be assigned to type {self}')


@dataclass(frozen=True)
class Param:
    name: str
    type: Type

    def __str__(self) -> str:
        return f'{self.name}: {self.type}'


@dataclass(frozen=True)
class Params(Sized, Iterable[Param]):
    _params: Sequence[Param] = field(default_factory=list[Param])

    def __str__(self) -> str:
        return f'({", ".join(str(param) for param in self._params)})'

    def __len__(self) -> int:
        return len(self._params)

    def __iter__(self) -> Iterator[Param]:
        return iter(self._params)

    def __bool__(self) -> bool:
        return bool(self._params)


@dataclass(frozen=True)
class Signature:
    params_: Params
    return_: Type

    def __str__(self) -> str:
        return f'{self.params_}->{self.return_}'


@dataclass(frozen=True)
class Signatures(Sized, Iterable[Signature]):
    _signatures: Sequence[Signature] = field(default_factory=list[Signature])

    def __str__(self) -> str:
        return '|'.join(str(signature) for signature in self._signatures)

    def __len__(self) -> int:
        return len(self._signatures)

    def __iter__(self) -> Iterator[Signature]:
        return iter(self._signatures)

    def __bool__(self) -> bool:
        return bool(self._signatures)


@dataclass
class Var:
    type: Type

    def __str__(self) -> str:
        return str(self.type)


Scope = scope.Scope[Var]


@dataclass(frozen=True)
class MutableScope(scope.MutableScope[Var]):
    @classmethod
    def set(cls, lhs: Var, rhs: Var) -> None:
        lhs.type.check_assignable(rhs.type)
