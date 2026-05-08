"""Line truncation utilities for logslice."""

from __future__ import annotations

from typing import Iterable, Iterator

DEFAULT_MAX_LENGTH = 200
ELLIPSIS = "..."


def truncate_line(line: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """Truncate a single line to at most *max_length* characters.

    If the line (after stripping the trailing newline) exceeds *max_length*,
    it is cut and an ellipsis appended.  The trailing newline, if present, is
    preserved after truncation.
    """
    if max_length <= 0:
        raise ValueError("max_length must be a positive integer")

    has_newline = line.endswith("\n")
    body = line.rstrip("\n")

    if len(body) <= max_length:
        return line  # nothing to do

    truncated = body[:max_length] + ELLIPSIS
    return truncated + ("\n" if has_newline else "")


def truncate_lines(
    lines: Iterable[str],
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Iterator[str]:
    """Yield lines from *lines*, each truncated to *max_length* characters.

    Lines that are already short enough are yielded unchanged so that no
    unnecessary string objects are created.
    """
    for line in lines:
        yield truncate_line(line, max_length)


def truncate_lines_conditional(
    lines: Iterable[str],
    max_length: int | None,
) -> Iterator[str]:
    """Yield lines, applying truncation only when *max_length* is not None.

    This helper lets callers avoid a conditional at every call site.
    """
    if max_length is None:
        yield from lines
    else:
        yield from truncate_lines(lines, max_length)
