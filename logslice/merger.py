"""Merge multiple sorted log streams into a single time-ordered stream."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator, List, Optional, Tuple

from logslice.parser import extract_timestamp


def _keyed(stream_id: int, lines: Iterable[str]):
    """Yield (timestamp_or_None, stream_id, line) triples for heap ordering."""
    for line in lines:
        ts = extract_timestamp(line)
        # Use a high sentinel so lines without timestamps sort last
        key = ts.isoformat() if ts is not None else "\xff"
        yield (key, stream_id, line)


def merge_streams(*streams: Iterable[str]) -> Iterator[str]:
    """Merge N log streams, emitting lines in timestamp order.

    Lines without a detectable timestamp are emitted after all timestamped
    lines from the same relative position.  Within the same timestamp the
    original stream order is preserved (stable via stream_id).
    """
    iterables = [_keyed(i, s) for i, s in enumerate(streams)]
    for _key, _sid, line in heapq.merge(*iterables):
        yield line


def merge_sorted_buffers(
    buffers: List[List[str]],
    drop_duplicates: bool = False,
) -> Iterator[str]:
    """Merge pre-collected buffers, optionally dropping exact-duplicate lines."""
    seen: Optional[set] = set() if drop_duplicates else None
    for line in merge_streams(*buffers):
        if seen is not None:
            if line in seen:
                continue
            seen.add(line)
        yield line
