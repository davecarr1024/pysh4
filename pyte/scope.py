from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic,  Iterator, Mapping, MutableMapping, Optional, TypeVar
from . import errors


_Var_co = TypeVar('_Var_co', covariant=True)


@dataclass(frozen=True)
class Scope(Generic[_Var_co], Mapping[str, _Var_co]):
    _vars: MutableMapping[str, _Var_co] = field(
        default_factory=dict[str, _Var_co])
    parent: Optional['Scope[_Var_co]'] = field(kw_only=True, default=None)

    def __str__(self) -> str:
        return str(self.all_vars)

    def __len__(self) -> int:
        return len(self.all_vars)

    def __iter__(self) -> Iterator[str]:
        return iter(self.all_vars)

    def __getitem__(self, name: str) -> _Var_co:
        if name in self._vars:
            return self._vars[name]
        if self.parent is not None:
            return self.parent[name]
        raise errors.Error(msg=f'getting unknown var {name}')

    def __eq__(self, rhs: object) -> bool:
        return isinstance(rhs, type(self)) and self.all_vars == rhs.all_vars

    def __contains__(self, name: object) -> bool:
        return name in self._vars or (self.parent is not None and name in self.parent)

    @property
    def vars(self) -> Mapping[str, _Var_co]:
        return self._vars

    @property
    def all_vars(self) -> Mapping[str, _Var_co]:
        vars: Mapping[str, _Var_co] = {}
        if self.parent is not None:
            vars |= self.parent.all_vars
        vars |= self._vars
        return vars

    @staticmethod
    def default_scope() -> 'Scope[_Var_co]':
        return Scope[_Var_co]({})

    def as_child(self) -> 'Scope[_Var_co]':
        return Scope[_Var_co]({}, parent=self)

    def _del(self, name: str) -> None:
        if name in self._vars:
            del self._vars[name]
        elif self.parent is not None:
            self.parent._del(name)
        else:
            raise errors.Error(msg=f'deleting unknown var {name}')


_Var = TypeVar('_Var')


@dataclass(frozen=True)
class MutableScope(Generic[_Var], Scope[_Var], MutableMapping[str, _Var], ABC):
    @classmethod
    @abstractmethod
    def set(cls, lhs: _Var, rhs: _Var) -> None:
        ...

    def __setitem__(self, name: str, var: _Var) -> None:
        try:
            self.set(self[name], var)
        except errors.Error as error:
            raise errors.UnaryError(
                msg=f'unable to set var {name}', child=error) from error

    def __delitem__(self, name: str) -> None:
        self._del(name)

    def decl(self, name: str, var: _Var) -> None:
        if name in self._vars:
            raise errors.Error(msg=f'declaring duplicate var {name}')
        self._vars[name] = var
