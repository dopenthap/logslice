"""Rate limiting for log output — cap lines emitted per second."""

import time
from typing import Iterator


def _now() -> float:
    return time.monotonic()


def rate_limit_lines(
    lines: Iterator[str],
    max_per_second: float,
    *,
    _clock=None,
    _sleep=None,
) -> Iterator[str]:
    """Yield lines from *lines*, pausing to stay within *max_per_second*.

    If *max_per_second* is <= 0 the lines are yielded without any throttling.
    """
    if max_per_second <= 0:
        yield from lines
        return

    clock = _clock or _now
    sleep = _sleep or time.sleep

    interval = 1.0 / max_per_second
    next_allowed = clock()

    for line in lines:
        now = clock()
        wait = next_allowed - now
        if wait > 0:
            sleep(wait)
        yield line
        next_allowed = clock() + interval


def burst_limit_lines(
    lines: Iterator[str],
    burst_size: int,
    window_seconds: float,
    *,
    _clock=None,
    _sleep=None,
) -> Iterator[str]:
    """Yield lines, allowing at most *burst_size* lines per *window_seconds*.

    Once the burst is exhausted the iterator waits until the window resets.
    """
    if burst_size <= 0 or window_seconds <= 0:
        yield from lines
        return

    clock = _clock or _now
    sleep = _sleep or time.sleep

    window_start = clock()
    count_in_window = 0

    for line in lines:
        now = clock()
        elapsed = now - window_start
        if elapsed >= window_seconds:
            window_start = now
            count_in_window = 0

        if count_in_window >= burst_size:
            remaining = window_seconds - (clock() - window_start)
            if remaining > 0:
                sleep(remaining)
            window_start = clock()
            count_in_window = 0

        yield line
        count_in_window += 1
