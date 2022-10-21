from typing import Optional, Sequence
from core import lexer, parser, regex
from . import builtins_, statements, vals


def eval(input: str, scope: Optional[vals.Scope] = None) -> vals.Val:
    operators: Sequence[str] = [
        '(',
        ')',
        '{',
        '}',
        ',',
        '.',
        ';',
        '=',
        'def',
        'class',
        'return',
        'namespace',
        '+',
        '-',
        '*',
        '/',
        'and',
        'or',
    ]
    _, tokens = lexer.Lexer(

        **({
            operator: regex.literal(operator)
            for operator in operators
        } | dict(_ws=lexer.ReClass.whitespace(),
                 int=regex.load('[0-9]+'),
                 id=regex.load('(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*')))
    )(lexer.Scope({}), input)
    _, statements_ = parser.UntilEmpty[statements.Statement](
        statements.Statement.load,
    )(statements.Statement.default_scope(), tokens)
    scope = scope or vals.Scope({})
    for statement in statements_[:-1]:
        statement.eval(scope)
    if isinstance(statements_[-1], statements.Expr):
        return statements_[-1].value.eval(scope)
    statements_[-1].eval(scope)
    return builtins_.none
