from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True, kw_only=True)
class Error(Exception):
    msg: Optional[str] = None


@dataclass(frozen=True, kw_only=True)
class UnaryError(Error):
    child: Error


@dataclass(frozen=True, kw_only=True)
class NaryError(Error):
    children: Sequence[Error]
