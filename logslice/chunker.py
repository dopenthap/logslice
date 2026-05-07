"""Split log streams into fixed-size or time-based chunks."""

from __future__ import annotations

from typing import Generator, Iterable, List, Optional
from datetime import datetime, timedelta

from logslice.parser import extract_timestamp


def chunk_by_size(
    lines: Iterable[str],
    chunk_size: int,
) -> Generator[List[str], None, None]:
    """Yield successive chunks of up to *chunk_size* lines."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")

    bucket: List[str] = []
    for line in lines:
        bucket.append(line)
        if len(bucket) >= chunk_size:
            yield bucket
            bucket = []
    if bucket:
        yield bucket


def chunk_by_time(
    lines: Iterable[str],
    window_seconds: float,
) -> Generator[List[str], None, None]:
    """Yield chunks where all lines fall within *window_seconds* of the
    first timestamped line in that chunk.

    Lines without a parseable timestamp are appended to the current chunk
    without triggering a boundary.
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds must be > 0")

    window = timedelta(seconds=window_seconds)
    bucket: List[str] = []
    chunk_start: Optional[datetime] = None

    for line in lines:
        ts = extract_timestamp(line)

        if ts is None:
            # No timestamp — keep with current chunk
            bucket.append(line)
            continue

        if chunk_start is None:
            chunk_start = ts

        if ts - chunk_start > window:
            if bucket:
                yield bucket
            bucket = [line]
            chunk_start = ts
        else:
            bucket.append(line)

    if bucket:
        yield bucket
