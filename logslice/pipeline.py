"""Pipeline orchestration for log processing with stats collection."""

from datetime import datetime
from typing import IO, Iterator, Optional

from logslice.filter import filter_lines
from logslice.formatter import format_line
from logslice.output import write_output
from logslice.parser import parse_line
from logslice.stats import LogStats
from logslice.reporter import write_stats


def _iter_with_stats(
    lines: Iterator[str],
    pattern: Optional[str],
    start: Optional[datetime],
    end: Optional[datetime],
    stats: LogStats,
) -> Iterator[tuple[str, int]]:
    """Yield (line, line_number) for matching lines while updating stats."""
    for lineno, raw in enumerate(lines, start=1):
        entry = parse_line(raw)
        ts = entry.get("timestamp") if entry else None

        if entry is None:
            stats.record_error()
            continue

        matched = True
        if pattern and not _matches(raw, pattern):
            matched = False
        if start and (ts is None or ts < start):
            matched = False
        if end and (ts is None or ts > end):
            matched = False

        stats.record_line(matched=matched, timestamp=ts if matched else None)

        if matched:
            yield raw, lineno


def _matches(line: str, pattern: str) -> bool:
    from logslice.parser import matches_pattern
    return matches_pattern(line, pattern)


def run_pipeline(
    source: IO[str],
    dest: IO[str],
    *,
    pattern: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    fmt: str = "plain",
    show_numbers: bool = False,
    show_stats: bool = False,
    stats_fmt: str = "plain",
    stats_stream: Optional[IO[str]] = None,
) -> LogStats:
    """Run the full log-slice pipeline and return collected stats."""
    stats = LogStats()
    stats.start_time = datetime.now()

    matched = _iter_with_stats(source, pattern, start, end, stats)
    write_output(
        ((line, lineno) for line, lineno in matched),
        dest,
        fmt=fmt,
        show_numbers=show_numbers,
    )

    stats.end_time = datetime.now()

    if show_stats:
        target = stats_stream or dest
        write_stats(stats, target, fmt=stats_fmt)

    return stats
