"""Diagnostics for strict ``json.loads`` failures (log + exception messages)."""

from __future__ import annotations

import json


def preview_text_for_log(text: str, *, head: int = 500, tail: int = 240) -> str:
    """Truncated repr for logs; avoids dumping megabyte-long model outputs."""
    if text is None:
        return "(None)"
    if not text:
        return "(empty)"
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(t) <= head + tail + 60:
        return repr(t)
    omitted = len(t) - head - tail
    return repr(t[:head]) + f"...<+{omitted} chars>..." + repr(t[-tail:])


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
