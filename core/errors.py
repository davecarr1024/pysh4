from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True, kw_only=True, repr=False)
class Error(Exception):
    msg: Optional[str] = None

    @classmethod
    def _repr(cls, class_name: Optional[str] = None, **kwargs: Optional[Any]) -> str:
        output = f'{class_name or cls.__name__}('
        output += ', '.join([f'{name}={repr(val)}' for name,
                            val in kwargs.items() if val is not None])
        output += ')'
        return output

    def _repr_args(self) -> Mapping[str, Optional[Any]]:
        return dict(msg=self.msg or None)

    def __repr__(self) -> str:
        return self._repr(**self._repr_args())

    def __str__(self) -> str:
        return repr(self)


@dataclass(frozen=True, kw_only=True)
class UnaryError(Error):
    child: Error

    def _repr_args(self) -> Mapping[str, Optional[Any]]:
        return super()._repr_args() | dict(child=self.child)


@dataclass(frozen=True, kw_only=True)
class NaryError(Error):
    children: Sequence[Error]

    def _repr_args(self) -> Mapping[str, Optional[Any]]:
        return super()._repr_args() | dict(children=self.children or None)
