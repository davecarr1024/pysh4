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
class _ValueObject(_Object, Generic[_Value]):
    value: _Value

    def __repr__(self) -> str:
        return repr(self.value)

    @staticmethod
    def valify(val: Any) -> vals.Val:
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
        return _ValueObject.valify(self.func(self.extractor(list(args)[0].value)))


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
        return _ValueObject.valify(self.func(lhs, rhs))


class IntObject(_ValueObject[int]):
    @staticmethod
    def intify(val: vals.Val) -> int:
        if not isinstance(val, IntObject):
            raise errors.Error(msg=f'unintifiable val {val}')
        return val.value


IntClass = _Class(
    'int',
    vals.Scope({
        '__add__': funcs.BindableFunc(_BinaryFunc(operator.add, IntObject.intify, IntObject.intify)),
        '__sub__': funcs.BindableFunc(_BinaryFunc(operator.sub, IntObject.intify, IntObject.intify)),
        '__mul__': funcs.BindableFunc(_BinaryFunc(operator.mul, IntObject.intify, IntObject.intify)),
        '__div__': funcs.BindableFunc(_BinaryFunc(operator.floordiv, IntObject.intify, IntObject.intify)),
        '__eq__': funcs.BindableFunc(_BinaryFunc(operator.eq, IntObject.intify, IntObject.intify)),
        '__lt__': funcs.BindableFunc(_BinaryFunc(operator.lt, IntObject.intify, IntObject.intify)),
        '__le__': funcs.BindableFunc(_BinaryFunc(operator.le, IntObject.intify, IntObject.intify)),
        '__gt__': funcs.BindableFunc(_BinaryFunc(operator.gt, IntObject.intify, IntObject.intify)),
        '__ge__': funcs.BindableFunc(_BinaryFunc(operator.ge, IntObject.intify, IntObject.intify)),
        '__bool__': funcs.BindableFunc(_UnaryFunc(bool, IntObject.intify)),
    }),
    IntObject,
)


def int_(value: int) -> vals.Object:
    return IntClass.instantiate(value)


class FloatObject(_ValueObject[float]):
    '''float builtin'''

    def __eq__(self, rhs: 'FloatObject') -> bool:
        return abs(self.value - rhs.value) < 1e-5


@ dataclass(frozen=True)
class _FloatFunc(_Func, ABC):
    name: str
    func: Callable[[float, float], float]
    return_factory: Callable[[Any], vals.Val] = lambda val: int_(val)

    @ property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    @ staticmethod
    def _float_arg(arg: vals.Val) -> FloatObject:
        if not isinstance(arg, FloatObject):
            raise errors.Error(msg=f'invalid float func arg {arg}')
        return arg

    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        self_ = self._float_arg(args['self']).value
        rhs = self._float_arg(args['rhs']).value
        return self.return_factory(self.func(self_, rhs))


FloatClass = _Class(
    'float',
    vals.Scope({
        '__add__': funcs.BindableFunc(_FloatFunc('__add__', operator.add)),
        '__sub__': funcs.BindableFunc(_FloatFunc('__sub__', operator.sub)),
        '__mul__': funcs.BindableFunc(_FloatFunc('__mul__', operator.mul)),
        '__div__': funcs.BindableFunc(_FloatFunc('__div__', operator.truediv)),
        '__eq__': funcs.BindableFunc(_FloatFunc('__eq__', operator.eq, lambda val: bool_(val))),
        '__lt__': funcs.BindableFunc(_FloatFunc('__lt__', operator.lt, lambda val: bool_(val))),
        '__le__': funcs.BindableFunc(_FloatFunc('__le__', operator.le, lambda val: bool_(val))),
        '__gt__': funcs.BindableFunc(_FloatFunc('__gt__', operator.gt, lambda val: bool_(val))),
        '__ge__': funcs.BindableFunc(_FloatFunc('__ge__', operator.ge, lambda val: bool_(val))),
    }),
    FloatObject,
)


def float_(value: float) -> vals.Object:
    return FloatClass.instantiate(value)


class StrObject(_ValueObject[str]):
    '''str builtin'''


@ dataclass(frozen=True)
class _StrFunc(_Func, ABC):
    name: str
    func: Callable[[str, str], str]

    @ property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    @ staticmethod
    def _str_arg(arg: vals.Val) -> StrObject:
        if not isinstance(arg, StrObject):
            raise errors.Error(msg=f'invalid str func arg {arg}')
        return arg

    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        self_ = self._str_arg(args['self']).value
        rhs = self._str_arg(args['rhs']).value
        return str_(self.func(self_, rhs))


StrClass = _Class(
    'str',
    vals.Scope({
        '__add__': funcs.BindableFunc(_StrFunc('__add__', operator.add)),
    }),
    StrObject,
)


def str_(value: str) -> vals.Object:
    return StrClass.instantiate(value)


class BoolObject(_ValueObject[bool]):
    '''bool builtin'''

    @ staticmethod
    def boolify(scope: vals.Scope, val: vals.Val) -> bool:
        if isinstance(val, BoolObject):
            return val.value
        if '__bool__' in val:
            return BoolObject.boolify(scope, val['__bool__'](scope,  vals.Args([])))
        raise errors.Error(msg=f'unboolifiable val {val}')


@ dataclass(frozen=True)
class _BoolFunc(_Func, ABC):
    name: str
    func: Callable[[bool, bool], bool]

    @ property
    def params(self) -> params.Params:
        return params.Params([params.Param('self'), params.Param('rhs')])

    @ staticmethod
    def _bool_arg(arg: vals.Val) -> BoolObject:
        if not isinstance(arg, BoolObject):
            raise errors.Error(msg=f'invalid bool func arg {arg}')
        return arg

    def apply(self, scope: vals.Scope, args: vals.Scope) -> vals.Val:
        self_ = self._bool_arg(args['self']).value
        rhs = self._bool_arg(args['rhs']).value
        return bool_(self.func(self_, rhs))


BoolClass = _Class(
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


NoneClass = _Class(
    'NoneType',
    vals.Scope({}),
    NoneObject,
)

none = NoneClass.instantiate()
