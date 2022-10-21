from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass(frozen=True, kw_only=True, repr=False)
class Error(Exception):
    msg: Optional[str] = None

    def _repr_line(self) -> str:
        if self.msg is not None:
            return f'msg={repr(self.msg)}'
        return ''

    def _repr(self, indent: int) -> str:
        return f'\n{"  "*indent}{self._repr_line()}'

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return self._repr(0)


@dataclass(frozen=True, kw_only=True, repr=False)
class NaryError(Error):
    children: Sequence[Error] = field(default_factory=list)

    def _repr(self, indent: int) -> str:
        s = Error._repr(self, indent)
        for child in self.children:
            s += child._repr(indent+1)
        return s

    def __repr__(self) -> str:
        return self._repr(0)


@dataclass(frozen=True, kw_only=True, repr=False)
class UnaryError(Error):
    child: Error

    def _repr(self, indent: int) -> str:
        return Error._repr(self, indent) + self.child._repr(indent+1)

    def __repr__(self) -> str:
        return self._repr(0)
