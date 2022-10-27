from abc import ABC, abstractmethod
import operator
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Mapping, Type, TypeVar
from . import errors, funcs, params, vals


@dataclass(frozen=True)
class _Class(vals.AbstractClass):
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


@dataclass(frozen=True, repr=False)
class _ValueObject(_Object, Generic[_Value], ABC):
    value: _Value

    def __repr__(self) -> str:
        return repr(self.value)

    @staticmethod
    def to_val(val: Any) -> vals.Val:
        ctors: Mapping[Type[Any], Callable[[Any], vals.Val]] = {
            bool: bool_,
            int: int_,
            float: float_,
            str: str_,
            type(None): lambda _: none,
        }
        if type(val) not in ctors:
            raise errors.Error(msg=f'unvalifiable val {val}')
        return ctors[type(val)](val)

    @classmethod
    @abstractmethod
    def from_val(cls, val: vals.Val) -> Any:
        ...


_Extractor = Callable[[vals.Val], Any]


@dataclass(frozen=True)
class _UnaryFunc(funcs.AbstractFunc):
    func: Callable[[Any], Any]
    extractor: _Extractor

    @property
    def params(self) -> params.Params:
        return params.Params([params.Param('self')])

    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        if len(args) != 1:
            raise errors.Error(msg=f'expected 1 arg got {len(args)}')
        return _ValueObject.to_val(self.func(self.extractor(list(args)[0].value)))


@dataclass(frozen=True)
class _BinaryFunc(funcs.AbstractFunc):
    func: Callable[[Any, Any], Any]
    lhs_extractor: _Extractor
    rhs_extractor: _Extractor

    @property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        if len(args) != 2:
            raise errors.Error(msg=f'expected 2 arg got {len(args)}')
        lhs_val, rhs_val = (arg.value for arg in args)
        lhs = self.lhs_extractor(lhs_val)
        rhs = self.rhs_extractor(rhs_val)
        return _ValueObject.to_val(self.func(lhs, rhs))


class IntObject(_ValueObject[int]):
    @classmethod
    def from_val(cls, val: vals.Val) -> int:
        if not isinstance(val, IntObject):
            raise errors.Error(msg=f'unintifiable val {val}')
        return val.value


IntClass = _Class(
    'int',
    vals.Scope({
        '__add__': funcs.BindableFunc(_BinaryFunc(operator.add, IntObject.from_val, IntObject.from_val)),
        '__sub__': funcs.BindableFunc(_BinaryFunc(operator.sub, IntObject.from_val, IntObject.from_val)),
        '__mul__': funcs.BindableFunc(_BinaryFunc(operator.mul, IntObject.from_val, IntObject.from_val)),
        '__div__': funcs.BindableFunc(_BinaryFunc(operator.floordiv, IntObject.from_val, IntObject.from_val)),
        '__eq__': funcs.BindableFunc(_BinaryFunc(operator.eq, IntObject.from_val, IntObject.from_val)),
        '__lt__': funcs.BindableFunc(_BinaryFunc(operator.lt, IntObject.from_val, IntObject.from_val)),
        '__le__': funcs.BindableFunc(_BinaryFunc(operator.le, IntObject.from_val, IntObject.from_val)),
        '__gt__': funcs.BindableFunc(_BinaryFunc(operator.gt, IntObject.from_val, IntObject.from_val)),
        '__ge__': funcs.BindableFunc(_BinaryFunc(operator.ge, IntObject.from_val, IntObject.from_val)),
        '__bool__': funcs.BindableFunc(_UnaryFunc(bool, IntObject.from_val)),
    }),
    IntObject,
)


def int_(value: int) -> vals.Object:
    return IntClass.instantiate(value)


class FloatObject(_ValueObject[float]):
    '''float builtin'''

    def __eq__(self, rhs: 'FloatObject') -> bool:
        return abs(self.value - rhs.value) < 1e-5

    @classmethod
    def from_val(cls, val: vals.Val) -> float:
        if not isinstance(val, FloatObject):
            raise errors.Error(msg=f'unfloatifiable val {val}')
        return val.value


FloatClass = _Class(
    'float',
    vals.Scope({
        '__add__': funcs.BindableFunc(_BinaryFunc(operator.add, FloatObject.from_val, FloatObject.from_val)),
        '__sub__': funcs.BindableFunc(_BinaryFunc(operator.sub, FloatObject.from_val, FloatObject.from_val)),
        '__mul__': funcs.BindableFunc(_BinaryFunc(operator.mul, FloatObject.from_val, FloatObject.from_val)),
        '__div__': funcs.BindableFunc(_BinaryFunc(operator.truediv, FloatObject.from_val, FloatObject.from_val)),
        '__eq__': funcs.BindableFunc(_BinaryFunc(operator.eq, FloatObject.from_val, FloatObject.from_val)),
        '__lt__': funcs.BindableFunc(_BinaryFunc(operator.lt, FloatObject.from_val, FloatObject.from_val)),
        '__le__': funcs.BindableFunc(_BinaryFunc(operator.le, FloatObject.from_val, FloatObject.from_val)),
        '__gt__': funcs.BindableFunc(_BinaryFunc(operator.gt, FloatObject.from_val, FloatObject.from_val)),
        '__ge__': funcs.BindableFunc(_BinaryFunc(operator.ge, FloatObject.from_val, FloatObject.from_val)),
        '__bool__': funcs.BindableFunc(_UnaryFunc(bool, FloatObject.from_val)),
    }),
    FloatObject,
)


def float_(value: float) -> vals.Object:
    return FloatClass.instantiate(value)


class StrObject(_ValueObject[str]):
    @classmethod
    def from_val(cls, val: vals.Val) -> str:
        if not isinstance(val, StrObject):
            raise errors.Error(msg=f'unstrifiable val {val}')
        return val.value


StrClass = _Class(
    'str',
    vals.Scope({
        '__add__': funcs.BindableFunc(_BinaryFunc(operator.add, StrObject.from_val, StrObject.from_val)),
        '__bool__': funcs.BindableFunc(_UnaryFunc(bool, StrObject.from_val)),
    }),
    StrObject,
)


def str_(value: str) -> vals.Object:
    return StrClass.instantiate(value)


class BoolObject(_ValueObject[bool]):
    @classmethod
    def from_val(cls, val: vals.Val) -> bool:
        if not isinstance(val, BoolObject):
            raise errors.Error(msg=f'unboolifiable val {val}')
        return val.value

    @staticmethod
    def boolify(scope: vals.Scope, val: vals.Val) -> bool:
        if isinstance(val, BoolObject):
            return val.value
        if '__bool__' in val:
            return BoolObject.boolify(scope, val['__bool__'](scope,  vals.Args([])))
        raise errors.Error(msg=f'unboolifiable val {val}')


BoolClass = _Class(
    'bool',
    vals.Scope({
        '__and__': funcs.BindableFunc(_BinaryFunc(operator.and_, BoolObject.from_val, BoolObject.from_val)),
        '__or__': funcs.BindableFunc(_BinaryFunc(operator.or_, BoolObject.from_val, BoolObject.from_val)),
    }),
    BoolObject,
)


def bool_(value: bool) -> vals.Object:
    return BoolClass.instantiate(value)


true = bool_(True)
false = bool_(False)


class NoneObject(_Object):
    '''none builtin'''


NoneClass = _Class(
    'NoneType',
    vals.Scope({}),
    NoneObject,
)

none = NoneClass.instantiate()
