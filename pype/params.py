from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence, Sized
from core import lexer, parser
from . import errors, vals


@dataclass(frozen=True, repr=False)
class Param:
    name: str

    def __repr__(self) -> str:
        return self.name

    def bind(self, scope: vals.Scope, arg: vals.Arg) -> None:
        scope[self.name] = arg.value

    @staticmethod
    def load(state: lexer.TokenStream) -> parser.StateAndResult['Param']:
        state, name = parser.get_token_value(state, 'id')
        return state, Param(name)


@dataclass(frozen=True, repr=False)
class Params(Iterable[Param], Sized):
    _params: Sequence[Param]

    def __repr__(self) -> str:
        return f'({", ".join(str(param) for param in self._params)})'

    def __len__(self) -> int:
        return len(self._params)

    def __iter__(self) -> Iterator[Param]:
        return iter(self._params)

    @property
    def tail(self) -> 'Params':
        if len(self._params) == 0:
            raise errors.Error(msg='empty params')
        return Params(self._params[1:])

    def bind(self, scope: vals.Scope, args: vals.Args) -> vals.Scope:
        '''bind the given args in a new child scope'''
        if len(self) != len(args):
            raise errors.Error(
                msg=f'param count mismatch: expected {len(self)} but got {len(args)}')
        scope = scope.as_child()
        for param, arg in zip(self, args):
            param.bind(scope, arg)
        return scope

    @staticmethod
    def load(state: lexer.TokenStream) -> parser.StateAndResult['Params']:
        state = parser.consume_token(state, '(')

        def load_params(state: lexer.TokenStream) -> parser.StateAndMultipleResult[Param]:
            state, head = Param.load(state)

            def load_tail(_: parser.Scope[Param], state: lexer.TokenStream) -> parser.StateAndResult[Param]:
                state = parser.consume_token(state, ',')
                return Param.load(state)

            state, tail = parser.ZeroOrMore[Param](
                load_tail)(parser.Scope[Param]({}), state)
            return state, [head] + list(tail)

        params: Sequence[Param] = []
        try:
            state, params = load_params(state)
        except errors.Error:
            pass
        state = parser.consume_token(state, ')')
        return state, Params(params)
