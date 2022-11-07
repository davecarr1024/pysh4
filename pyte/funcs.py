from abc import ABC, abstractmethod
from . import types_, vals


class AbstractFunc(vals.Val, types_.Type, ABC):
    @property
    def signatures(self) -> types_.Signatures:
        return types_.Signatures([self.signature])

    @property
    @abstractmethod
    def signature(self) -> types_.Signature:
        ...

    @abstractmethod
    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        ...
