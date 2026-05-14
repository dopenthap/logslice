"""Sliding and tumbling window aggregation over log lines."""

from collections import deque
from typing import Callable, Deque, Generator, Iterable, List, Optional, Tuple


def tumbling_window(
    lines: Iterable[str],
    size: int,
) -> Generator[List[str], None, None]:
    """Yield non-overlapping windows of exactly `size` lines.

    The final window may be smaller than `size` if lines are exhausted.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    bucket: List[str] = []
    for line in lines:
        bucket.append(line)
        if len(bucket) == size:
            yield bucket
            bucket = []
    if bucket:
        yield bucket


def sliding_window(
    lines: Iterable[str],
    size: int,
    step: int = 1,
) -> Generator[List[str], None, None]:
    """Yield overlapping windows of `size` lines, advancing by `step`."""
    if size <= 0:
        raise ValueError("size must be positive")
    if step <= 0:
        raise ValueError("step must be positive")
    buf: Deque[str] = deque()
    emit_at = size
    count = 0
    for line in lines:
        buf.append(line)
        count += 1
        if len(buf) > size:
            buf.popleft()
        if count == emit_at and len(buf) == size:
            yield list(buf)
            emit_at += step
    # emit a final partial window if we never reached a full one
    if buf and count < size:
        yield list(buf)


def window_reduce(
    windows: Iterable[List[str]],
    fn: Callable[[List[str]], str],
) -> Generator[str, None, None]:
    """Apply a reduction function to each window, yielding one result per window."""
    for window in windows:
        yield fn(window)
