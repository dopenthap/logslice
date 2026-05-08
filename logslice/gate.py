"""Gating utilities — pause / resume a line stream based on external signals."""

from typing import Callable, Iterator, Optional


def gate_lines(
    lines: Iterator[str],
    should_pass: Callable[[str], bool],
) -> Iterator[str]:
    """Yield only lines for which *should_pass* returns True.

    Unlike a simple filter this is intended for *dynamic* predicates that may
    change state between calls (e.g. a toggle driven by a signal handler).
    """
    for line in lines:
        if should_pass(line):
            yield line


def toggle_gate(
    lines: Iterator[str],
    start_pattern: Optional[str] = None,
    stop_pattern: Optional[str] = None,
) -> Iterator[str]:
    """Yield lines between *start_pattern* and *stop_pattern* markers.

    - If *start_pattern* is None, yielding begins immediately.
    - If *stop_pattern* is None, yielding continues until the stream ends.
    - The marker lines themselves are included in the output.
    """
    import re

    active = start_pattern is None

    for line in lines:
        if not active and start_pattern and re.search(start_pattern, line):
            active = True

        if active:
            yield line

        if active and stop_pattern and re.search(stop_pattern, line):
            active = False


def limit_lines(
    lines: Iterator[str],
    max_lines: int,
) -> Iterator[str]:
    """Yield at most *max_lines* lines then stop consuming the source."""
    if max_lines <= 0:
        return
    count = 0
    for line in lines:
        yield line
        count += 1
        if count >= max_lines:
            break


def skip_lines(
    lines: Iterator[str],
    n: int,
) -> Iterator[str]:
    """Skip the first *n* lines then yield the rest."""
    skipped = 0
    for line in lines:
        if skipped < n:
            skipped += 1
            continue
        yield line
