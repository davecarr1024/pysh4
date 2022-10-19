from abc import ABC, abstractmethod
import operator
from dataclasses import dataclass, field
from typing import Callable, Generic, Type, TypeVar
from . import errors, funcs, params, vals


@dataclass(frozen=True)
class Class(vals.AbstractClass):
    _name: str
    _members: vals.Scope
    __object_type: Type['_Object']

    @property
    def name(self) -> str:
        return self._name

    @property
    def members(self) -> vals.Scope:
        return self._members

    @property
    def _object_type(self) -> Type['_Object']:
        return self.__object_type


@dataclass(frozen=True)
class _Object(vals.Object):
    # don't waste time deep comparing builtin objects
    class_: vals.AbstractClass = field(compare=False, repr=False)
    _members: vals.Scope = field(compare=False, repr=False)


class _Func(funcs.AbstractFunc, ABC):
    @abstractmethod
    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        ...

    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        return self.apply(scope, self.params.bind(vals.Scope(), args))


_Value = TypeVar('_Value')


@dataclass(frozen=True)
class _ValueObject(_Object, Generic[_Value]):
    value: _Value


@dataclass(frozen=True)
class IntObject(_ValueObject[int]):
    ...


@dataclass(frozen=True)
class _IntFunc(_Func, ABC):
    name: str
    func: Callable[[int, int], int]

    @property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    @staticmethod
    def _int_arg(arg: vals.Val) -> IntObject:
        if not isinstance(arg, IntObject):
            raise errors.Error(msg=f'invalid int func arg {arg}')
        return arg

    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        self_ = self._int_arg(args['self']).value
        rhs = self._int_arg(args['rhs']).value
        return int_(self.func(self_, rhs))


IntClass = Class(
    'int',
    vals.Scope({
        '__add__': funcs.BindableFunc(_IntFunc('__add__', operator.add)),
        '__sub__': funcs.BindableFunc(_IntFunc('__sub__', operator.sub)),
        '__mul__': funcs.BindableFunc(_IntFunc('__mul__', operator.mul)),
        '__div__': funcs.BindableFunc(_IntFunc('__div__', operator.floordiv)),
    }),
    IntObject,
)


def int_(value: int) -> vals.Object:
    return IntClass.instantiate(value)


@dataclass(frozen=True)
class FloatObject(_ValueObject[float]):
    '''float builtin'''


@dataclass(frozen=True)
class _FloatFunc(_Func, ABC):
    name: str
    func: Callable[[float, float], float]

    @property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    @staticmethod
    def _float_arg(arg: vals.Val) -> FloatObject:
        if not isinstance(arg, FloatObject):
            raise errors.Error(msg=f'invalid float func arg {arg}')
        return arg

    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        self_ = self._float_arg(args['self']).value
        rhs = self._float_arg(args['rhs']).value
        return float_(self.func(self_, rhs))


FloatClass = Class(
    'float',
    vals.Scope({
        '__add__': funcs.BindableFunc(_FloatFunc('__add__', operator.add)),
        '__sub__': funcs.BindableFunc(_FloatFunc('__sub__', operator.sub)),
        '__mul__': funcs.BindableFunc(_FloatFunc('__mul__', operator.mul)),
        '__div__': funcs.BindableFunc(_FloatFunc('__div__', operator.truediv)),
    }),
    FloatObject,
)


def float_(value: float) -> vals.Object:
    return FloatClass.instantiate(value)


@dataclass(frozen=True)
class StrObject(_ValueObject[str]):
    '''str builtin'''


@dataclass(frozen=True)
class _StrFunc(_Func, ABC):
    name: str
    func: Callable[[str, str], str]

    @property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    @staticmethod
    def _str_arg(arg: vals.Val) -> StrObject:
        if not isinstance(arg, StrObject):
            raise errors.Error(msg=f'invalid str func arg {arg}')
        return arg

    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        self_ = self._str_arg(args['self']).value
        rhs = self._str_arg(args['rhs']).value
        return str_(self.func(self_, rhs))


StrClass = Class(
    'str',
    vals.Scope({
        '__add__': funcs.BindableFunc(_StrFunc('__add__', operator.add)),
    }),
    StrObject,
)


def str_(value: str) -> vals.Object:
    return StrClass.instantiate(value)


@dataclass(frozen=True)
class BoolObject(_ValueObject[bool]):
    '''bool builtin'''


@dataclass(frozen=True)
class _BoolFunc(_Func, ABC):
    name: str
    func: Callable[[bool, bool], bool]

    @property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    @staticmethod
    def _bool_arg(arg: vals.Val) -> BoolObject:
        if not isinstance(arg, BoolObject):
            raise errors.Error(msg=f'invalid bool func arg {arg}')
        return arg

    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        self_ = self._bool_arg(args['self']).value
        rhs = self._bool_arg(args['rhs']).value
        return bool_(self.func(self_, rhs))


BoolClass = Class(
    'bool',
    vals.Scope({
        '__and__': funcs.BindableFunc(_BoolFunc('__and__', operator.and_)),
        '__or__': funcs.BindableFunc(_BoolFunc('__or__', operator.or_)),
    }),
    BoolObject,
)


def bool_(value: bool) -> vals.Object:
    return BoolClass.instantiate(value)


true = bool_(True)
false = bool_(False)


class NoneObject(_Object):
    '''none builtin'''


NoneClass = Class(
    'NoneType',
    vals.Scope({}),
    NoneObject,
)

none = NoneClass.instantiate()
