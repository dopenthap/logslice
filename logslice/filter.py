"""Filter log lines by regex pattern and/or time range."""

from datetime import datetime
from typing import Iterable, Iterator, Optional

from logslice.parser import matches_pattern, parse_line


def filter_lines(
    lines: Iterable[str],
    pattern: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    ignore_case: bool = False,
) -> Iterator[str]:
    """
    Yield log lines that satisfy all provided filters.

    Args:
        lines:       Iterable of raw log line strings.
        pattern:     Optional regex; only matching lines are kept.
        start:       Optional lower bound for timestamp filtering (inclusive).
        end:         Optional upper bound for timestamp filtering (inclusive).
        ignore_case: Whether regex matching is case-insensitive.
    """
    for line in lines:
        if not line.strip():
            continue

        parsed = parse_line(line)

        # Regex filter
        if pattern is not None:
            if not matches_pattern(parsed["raw"], pattern, ignore_case):
                continue

        # Time-range filter — only applied when the line has a timestamp
        ts = parsed["timestamp"]
        if (start is not None or end is not None) and ts is not None:
            if start is not None and ts < start:
                continue
            if end is not None and ts > end:
                continue

        yield parsed["raw"]
