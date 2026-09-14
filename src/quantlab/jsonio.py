"""Strict finite, unambiguous JSON at file/upload boundaries. Never executable data."""

import json
import math


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key is ambiguous")
        result[key] = value
    return result


def _constant(_value):
    raise ValueError("Nonfinite JSON number is not permitted")


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Nonfinite JSON number is not permitted")
    return result


def loads(text):
    if not isinstance(text, (str, bytes)) or len(text) > 25_000_000:
        raise ValueError("JSON input must be text within the 25 MB local limit")
    try:
        value = json.loads(
            text, object_pairs_hook=_object, parse_constant=_constant, parse_float=_float
        )
        pending = [(value, 0)]
        while pending:
            item, depth = pending.pop()
            if depth > 64:
                raise ValueError("JSON nesting exceeds 64 levels")
            if isinstance(item, dict):
                pending.extend((child, depth + 1) for child in item.values())
            elif isinstance(item, list):
                pending.extend((child, depth + 1) for child in item)
        return value
    except RecursionError as exc:
        raise ValueError("JSON nesting exceeds the local parser limit") from exc
