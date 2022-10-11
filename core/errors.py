from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass(frozen=True, kw_only=True)
class Error(Exception):
    msg: Optional[str] = None
    rule_name: Optional[str] = None
    children: Sequence['Error'] = field(default_factory=list)
