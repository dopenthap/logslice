"""Provide surrounding context lines for matched log entries."""

from collections import deque
from typing import Generator, Iterable, Tuple


def context_lines(
    lines: Iterable[str],
    before: int = 0,
    after: int = 0,
    predicate=None,
) -> Generator[Tuple[str, bool], None, None]:
    """Yield ``(line, is_match)`` tuples with optional before/after context.

    Args:
        lines: Iterable of raw log lines.
        before: Number of lines to emit before each match.
        after: Number of lines to emit after each match.
        predicate: Callable ``(line) -> bool`` that identifies matches.
                   When ``None`` every line is treated as a match.

    Yields:
        Tuples of ``(line, is_match)`` where *is_match* is ``True`` for
        lines that satisfied *predicate* and ``False`` for context-only lines.
    """
    if predicate is None:
        predicate = lambda _: True  # noqa: E731

    before = max(0, before)
    after = max(0, after)

    buf: deque[str] = deque(maxlen=before)
    pending_after: int = 0
    emitted: set[int] = set()
    window: list[Tuple[str, bool]] = []  # (line, is_match)

    # Buffer everything so we can look ahead for 'after' context.
    all_lines = list(lines)
    n = len(all_lines)
    match_indices: set[int] = {
        i for i, ln in enumerate(all_lines) if predicate(ln)
    }

    emitted_indices: set[int] = set()
    for idx in sorted(match_indices):
        start = max(0, idx - before)
        end = min(n - 1, idx + after)
        for j in range(start, end + 1):
            emitted_indices.add(j)

    for i, line in enumerate(all_lines):
        if i in emitted_indices:
            yield (line, i in match_indices)


def collect_context(
    lines: Iterable[str],
    before: int = 0,
    after: int = 0,
    predicate=None,
) -> list:
    """Convenience wrapper returning a list of ``(line, is_match)`` tuples."""
    return list(context_lines(lines, before=before, after=after, predicate=predicate))
