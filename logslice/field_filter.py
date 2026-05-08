"""Filter log lines based on extracted field values.

Complements transformer.py by allowing callers to keep or drop
lines whose fields satisfy simple equality / regex predicates.
"""

import re
from typing import Callable, Iterable, Iterator, Optional

from logslice.transformer import extract_field, parse_kv


def _compile(pattern: str) -> re.Pattern:
    return re.compile(pattern)


def field_equals(
    lines: Iterable[str],
    index: int,
    value: str,
    sep: str = " ",
) -> Iterator[str]:
    """Yield lines where the field at *index* equals *value*."""
    for line in lines:
        if extract_field(line, index, sep=sep) == value:
            yield line


def field_matches(
    lines: Iterable[str],
    index: int,
    pattern: str,
    sep: str = " ",
) -> Iterator[str]:
    """Yield lines where the field at *index* matches *pattern*."""
    rx = _compile(pattern)
    for line in lines:
        field = extract_field(line, index, sep=sep)
        if field is not None and rx.search(field):
            yield line


def kv_equals(
    lines: Iterable[str],
    key: str,
    value: str,
) -> Iterator[str]:
    """Yield lines that contain *key*=*value* as a kv pair."""
    for line in lines:
        pairs = parse_kv(line)
        if pairs.get(key) == value:
            yield line


def kv_matches(
    lines: Iterable[str],
    key: str,
    pattern: str,
) -> Iterator[str]:
    """Yield lines where the kv *key*'s value matches *pattern*."""
    rx = _compile(pattern)
    for line in lines:
        pairs = parse_kv(line)
        val = pairs.get(key)
        if val is not None and rx.search(val):
            yield line


def make_field_predicate(
    index: int,
    pattern: str,
    sep: str = " ",
) -> Callable[[str], bool]:
    """Return a predicate that tests a single line."""
    rx = _compile(pattern)

    def _pred(line: str) -> bool:
        field = extract_field(line, index, sep=sep)
        return field is not None and bool(rx.search(field))

    return _pred
