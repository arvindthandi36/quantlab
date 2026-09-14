"""Canonical, finite JSON and content fingerprints, independent of simulation type."""

import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path


def encode(value):
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"unsupported research JSON value: {type(value).__name__}")


def canonical(value) -> str:
    return json.dumps(
        value, default=encode, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def plain(value):
    return json.loads(canonical(value))


def _reject(value):
    raise ValueError(f"nonfinite JSON value: {value}")


def read_json(path: str | Path):
    return json.loads(Path(path).read_text(), parse_constant=_reject)


def write_new(path: str | Path, value) -> None:
    """Exclusive create prevents an old prediction/result being silently rewritten."""
    with Path(path).open("x", encoding="utf-8") as target:
        target.write(
            json.dumps(value, default=encode, sort_keys=True, indent=2, allow_nan=False)
        )
        target.write("\n")
