"""Deduplicate log lines based on exact or normalized content."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Iterator
from typing import Callable


# Strip timestamps and numeric tokens before hashing for fuzzy dedup
_NORMALIZE_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
    r"|\b\d+\b",
    re.ASCII,
)


def _exact_key(line: str) -> str:
    """Return the line itself as the dedup key."""
    return line.rstrip("\n")


def _normalized_key(line: str) -> str:
    """Strip timestamps and numbers, then hash to produce a stable key."""
    cleaned = _NORMALIZE_RE.sub("<X>", line.rstrip("\n"))
    return hashlib.md5(cleaned.encode(), usedforsecurity=False).hexdigest()


def _make_key_fn(fuzzy: bool) -> Callable[[str], str]:
    return _normalized_key if fuzzy else _exact_key


def deduplicate(
    lines: Iterable[str],
    *,
    fuzzy: bool = False,
    count: bool = False,
) -> Iterator[str]:
    """Yield unique lines from *lines*.

    Parameters
    ----------
    lines:
        Source lines to deduplicate.
    fuzzy:
        When *True*, lines that differ only in timestamps or numbers are
        treated as duplicates.
    count:
        When *True*, append `` (xN)`` to each line that appeared more than
        once, showing how many times it was seen.
    """
    key_fn = _make_key_fn(fuzzy)
    seen: dict[str, tuple[str, int]] = {}  # key -> (first_line, occurrences)

    for line in lines:
        key = key_fn(line)
        if key in seen:
            first, n = seen[key]
            seen[key] = (first, n + 1)
        else:
            seen[key] = (line.rstrip("\n"), 1)

    for first_line, occurrences in seen.values():
        if count and occurrences > 1:
            yield f"{first_line} (x{occurrences})\n"
        else:
            yield first_line + "\n"
