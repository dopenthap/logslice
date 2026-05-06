"""Handles writing formatted output to a stream or file."""

import sys
from typing import Iterable, IO, Optional

from logslice.formatter import format_line, format_header, format_summary, DEFAULT_FORMAT


def write_lines(
    lines: Iterable[str],
    fmt: str = DEFAULT_FORMAT,
    show_line_numbers: bool = False,
    out: IO[str] = sys.stdout,
    show_summary: bool = False,
) -> int:
    """
    Write formatted lines to *out*.

    Returns the number of lines written.
    """
    header = format_header(fmt)
    if header:
        out.write(header + "\n")

    count = 0
    for line in lines:
        n: Optional[int] = count + 1 if show_line_numbers else None
        out.write(format_line(line, fmt=fmt, line_number=n) + "\n")
        count += 1

    return count


def write_output(
    lines: Iterable[str],
    fmt: str = DEFAULT_FORMAT,
    show_line_numbers: bool = False,
    out: IO[str] = sys.stdout,
    total: Optional[int] = None,
    show_summary: bool = False,
) -> int:
    """High-level helper used by the CLI."""
    matched = write_lines(
        lines,
        fmt=fmt,
        show_line_numbers=show_line_numbers,
        out=out,
    )
    if show_summary and total is not None:
        out.write(format_summary(matched, total, fmt=fmt) + "\n")
    return matched
