"""Line transformation utilities for logslice.

Supports field extraction, key=value parsing, and simple
string replacements on log lines before output.
"""

import re
from typing import Callable, Iterable, Iterator, Optional


_KV_RE = re.compile(r'(\w+)=(["\']?)([^\s\'"]+)\2')


def extract_field(line: str, index: int, sep: str = " ") -> Optional[str]:
    """Return the field at *index* after splitting *line* on *sep*.

    Returns None when the index is out of range.
    """
    parts = line.rstrip("\n").split(sep)
    if index < 0 or index >= len(parts):
        return None
    return parts[index]


def parse_kv(line: str) -> dict:
    """Extract all key=value pairs from *line* into a dict."""
    return {m.group(1): m.group(3) for m in _KV_RE.finditer(line)}


def replace_field(
    line: str,
    pattern: str,
    replacement: str,
    count: int = 0,
) -> str:
    """Return *line* with regex *pattern* replaced by *replacement*.

    Preserves a trailing newline if the original line had one.
    """
    trailing = "\n" if line.endswith("\n") else ""
    result = re.sub(pattern, replacement, line.rstrip("\n"), count=count)
    return result + trailing


def make_transformer(
    *,
    pattern: Optional[str] = None,
    replacement: str = "",
    count: int = 0,
) -> Callable[[str], str]:
    """Return a single-argument transformer function.

    When *pattern* is None the transformer is a no-op.
    """
    if pattern is None:
        return lambda line: line
    return lambda line: replace_field(line, pattern, replacement, count=count)


def transform_lines(
    lines: Iterable[str],
    transformer: Callable[[str], str],
) -> Iterator[str]:
    """Apply *transformer* to every line in *lines*."""
    for line in lines:
        yield transformer(line)
