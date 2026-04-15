"""Diagnostics for strict ``json.loads`` failures (log + exception messages)."""

from __future__ import annotations

import json


def describe_json_decode_error(text: str, exc: json.JSONDecodeError) -> str:
    """
    Human-readable pointer to where parsing broke (line/col/pos + snippet + caret).

    Use when model output is truncated, has an unclosed string, or extra prose before `{`.
    """
    n = len(text)
    pos = min(max(0, int(exc.pos)), n)
    width = 80
    lo = max(0, pos - width)
    hi = min(n, pos + width)
    snippet = text[lo:hi]
    marker = " " * (pos - lo) + "^"
    return (
        f"JSONDecodeError pos={pos} line={exc.lineno} col={exc.colno} len={n}; "
        f"context:\n{snippet}\n{marker}"
    )
