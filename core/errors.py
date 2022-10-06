from dataclasses import dataclass, field
from typing import Optional, Sequence, final


@dataclass(frozen=True, kw_only=True)
@final
class Error(Exception):
    msg: Optional[str] = None
    rule_name: Optional[str] = None
    children: Sequence['Error'] = field(default_factory=list)

    def with_rule_name(self, rule_name: str) -> 'Error':
        return Error(msg=self.msg, children=self.children, rule_name=rule_name)
