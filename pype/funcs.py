from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from . import errors, params, vals


class AbstractFunc(vals.Val, ABC):
    @property
    @abstractmethod
    def params(self) -> params.Params:
        ...

    @abstractmethod
    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        ...


@dataclass(frozen=True)
class BindableFunc(AbstractFunc):
    func: AbstractFunc

    def __post_init__(self):
        if len(self.func.params) == 0:
            raise errors.Error(
                msg=f'unable to create bindable func from func {self.func} with 0 params')

    @property
    def params(self) -> params.Params:
        return self.func.params

    @property
    def can_bind(self) -> bool:
        return True

    def bind(self, object_: vals.Val) -> vals.Val:
        return BoundFunc(object_, self)

    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        return self.func(scope, args)


@dataclass(frozen=True)
class BoundFunc(AbstractFunc):
    object_: vals.Val = field(compare=False, repr=False)
    func: BindableFunc

    def __post_init__(self):
        if len(self.func.params) == 0:
            raise errors.Error(
                msg=f'unable to bind func {self.func} with 0 params')

    @property
    def params(self) -> params.Params:
        return self.func.params.tail

    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        return self.func(scope, args.prepend(vals.Arg(self.object_)))
