from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Mapping, Sequence, Sized, Type
from . import errors, scope, types_


class Val(ABC, Mapping[str, 'Val']):
    @property
    @abstractmethod
    def type(self) -> types_.Type:
        ...

    def members(self) -> 'Scope':
        return Scope({})

    def __iter__(self) -> Iterator[str]:
        return iter(self.members())

    def __len__(self) -> int:
        return len(self.members())

    def __getitem__(self, name: str) -> 'Val':
        return self.members()[name].value

    def __call__(self, scope: 'Scope', args: 'Args') -> 'Val':
        raise errors.Error(msg=f'calling uncallable {self}')


@dataclass(frozen=True)
class Arg:
    value: Val

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Args(Iterable[Arg], Sized):
    _args: Sequence[Arg]

    def __str__(self) -> str:
        return f'({", ".join(str(arg) for arg in self._args)})'

    def __len__(self) -> int:
        return len(self._args)

    def __iter__(self) -> Iterator[Arg]:
        return iter(self._args)

    def prepend(self, arg: Arg) -> 'Args':
        return Args([arg] + list(self._args))


@dataclass
class Var(types_.Var):
    value: Val

    def __str__(self) -> str:
        return f'{self.value}: {self.type}'

    def __post_init__(self):
        try:
            self.type.check_assignable(self.value.type)
        except errors.Error as error:
            raise errors.UnaryError(
                msg=f'invalid var {self}', child=error) from error


Scope = scope.Scope[Var]


@dataclass(frozen=True)
class MutableScope(scope.MutableScope[Var]):
    @classmethod
    def set(cls, lhs: Var, rhs: Var) -> None:
        types_.MutableScope.set(lhs, rhs)
        lhs.value = rhs.value


@dataclass(frozen=True)
class ClassType(types_.Type):
    @property
    def name(self) -> str:
        return 'Class'

    @property
    def signatures(self) -> types_.Signatures:
        return types_.Signatures()


class_type = ClassType()


@dataclass(frozen=True)
class AbstractClass(Val, types_.Type,  ABC):
    @property
    def type(self) -> types_.Type:
        return class_type

    @property
    @abstractmethod
    def _object_type(self) -> Type['Object']:
        return Object

    def instantiate(self, *args: Any, **kwargs: Any) -> 'Object':
        object_ = self._object_type(
            self, self.members().as_child(), *args, **kwargs)
        return object_

    def __call__(self, scope: Scope, args: Args) -> 'Object':
        object_ = self.instantiate()
        if '__init__' in object_:
            object_['__init__'](scope, args)
        return object_


@dataclass(frozen=True)
class Class(AbstractClass):
    _name: str
    _members: Scope

    @property
    def _object_type(self) -> Type['Object']:
        return Object

    @property
    def name(self) -> str:
        return self._name

    def members(self) -> Scope:
        return self._members


@dataclass(frozen=True)
class Object(Val):
    class_: AbstractClass
    _members: Scope

    def members(self) -> Scope:
        return self._members

    @property
    def type(self) -> types_.Type:
        return self.class_

    @property
    def signatures(self) -> types_.Signatures:
        if '__call__' in self:
            return self.members()['__call__'].type.signatures
        return types_.Signatures()

    def __call__(self, scope: Scope, args: Args) -> Val:
        if '__call__' not in self:
            raise errors.Error(msg=f'object {self} not callable')
        return self['__call__'](scope, args)
