from dataclasses import dataclass, field
from typing import Optional, Sequence, final


@dataclass(frozen=True, kw_only=True)
class Error(Exception):
    msg: Optional[str] = None


@dataclass(frozen=True, kw_only=True)
class UnaryError(Error):
    child: Error


@dataclass(frozen=True, kw_only=True)
class NaryError(Error):
    children: Error
