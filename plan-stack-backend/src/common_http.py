"""Shared Flask request/response helpers for Plan Stack and Assistant blueprints."""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Optional, TypeVar

from flask import jsonify, request

EnumT = TypeVar("EnumT", bound=Enum)


def bad_request(message: str):
    return jsonify({"error": message}), 400


def json_body_or_error():
    """Parse JSON body; reject null or empty body."""
    data = request.get_json()
    if not data:
        return None, bad_request("Invalid JSON body")
    return data, None


def parse_enum_or_error(
    enum_cls: type[EnumT],
    raw_value: Optional[str],
    *,
    field_name: str,
    normalizer: Optional[Callable[[str], str]] = None,
    choices_hint: Optional[str] = None,
) -> tuple[Optional[EnumT], Optional[Any]]:
    if raw_value is None:
        return None, None
    normalized = normalizer(raw_value) if normalizer else raw_value
    try:
        return enum_cls(normalized), None
    except ValueError:
        if choices_hint:
            return None, bad_request(
                f"Invalid {field_name}: {raw_value}. Must be one of: {choices_hint}"
            )
        return None, bad_request(f"Invalid {field_name}: {raw_value}")


def parse_bool_query_param(name: str) -> Optional[bool]:
    raw = request.args.get(name)
    if raw is None:
        return None
    return raw.lower() == "true"
