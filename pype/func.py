from dataclasses import dataclass
from . import errors, params, builtins_, statements, vals, funcs


@dataclass(frozen=True)
class Func(funcs.AbstractFunc):
    name: str
    _params: params.Params
    body: statements.Block

    @property
    def params(self) -> params.Params:
        return self._params

    def __call__(self, scope: vals.Scope, args: vals.Args) -> vals.Val:
        try:
            scope = self._params.bind(scope, args)
        except errors.Error as error:
            raise errors.Error(
                f'failed to bind params for func {self} with args {args}: {error}') from error
        result = self.body.eval(scope)
        if result.return_ is not None and result.return_.value is not None:
            return result.return_.value
        return builtins_.none


@dataclass(frozen=True)
class Decl(statements.Decl):
    _name: str
    params_: params.Params
    body: statements.Block

    @property
    def name(self) -> str:
        return self._name

    def value(self, scope: vals.Scope) -> statements.Decl.Value:
        return Decl.Value(Func(self.name, self.params_, self.body), statements.Result())
