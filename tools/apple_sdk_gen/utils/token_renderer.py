from __future__ import annotations

from ..models.symbol import Declaration, Token


def render_tokens(tokens: list[Token]) -> str:
    return "".join(t.text for t in tokens)


def render_declaration(decl: Declaration) -> str:
    return render_tokens(decl.tokens)
