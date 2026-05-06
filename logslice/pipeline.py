"""End-to-end pipeline: open a log file, filter lines, write formatted output."""

import sys
from datetime import datetime
from typing import Optional, IO

from logslice.filter import filter_lines
from logslice.output import write_output
from logslice.formatter import SUPPORTED_FORMATS, DEFAULT_FORMAT


def run_pipeline(
    source: IO[str],
    pattern: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    fmt: str = DEFAULT_FORMAT,
    show_line_numbers: bool = False,
    show_summary: bool = False,
    out: IO[str] = sys.stdout,
) -> int:
    """
    Filter *source* and write results to *out*.

    Returns the number of matched lines.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unknown format {fmt!r}")

    all_lines = list(source)
    total = len(all_lines)

    filtered = filter_lines(
        iter(all_lines),
        pattern=pattern,
        start=start,
        end=end,
    )

    matched = write_output(
        filtered,
        fmt=fmt,
        show_line_numbers=show_line_numbers,
        out=out,
        total=total,
        show_summary=show_summary,
    )
    return matched
