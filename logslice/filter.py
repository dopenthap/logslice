"""Line filtering utilities for logslice."""

from typing import Iterable, Iterator

from logslice.parser import extract_timestamp, matches_pattern
from logslice.sampler import sample_every_nth, sample_lines


def filter_lines(
    lines: Iterable[str],
    pattern: str | None = None,
    start: object = None,
    end: object = None,
    invert: bool = False,
    sample_rate: float | None = None,
    sample_nth: int | None = None,
    sample_seed: int | None = None,
) -> Iterator[str]:
    """Filter log lines by pattern, time range, and optional sampling.

    Args:
        lines: Raw log lines to process.
        pattern: Optional regex pattern; only matching lines are kept.
        start: Optional start datetime; lines before this are dropped.
        end: Optional end datetime; lines after this are dropped.
        invert: When True, keep lines that do NOT match the pattern.
        sample_rate: If set, randomly sample at this rate after filtering.
        sample_nth: If set, keep every nth line after filtering.
        sample_seed: Seed for the random sampler.

    Yields:
        Lines that pass all active filters.
    """
    filtered: Iterable[str] = _apply_filters(lines, pattern, start, end, invert)

    if sample_nth is not None:
        filtered = sample_every_nth(filtered, n=sample_nth)
    elif sample_rate is not None:
        filtered = sample_lines(filtered, rate=sample_rate, seed=sample_seed)

    yield from filtered


def _apply_filters(
    lines: Iterable[str],
    pattern: str | None,
    start: object,
    end: object,
    invert: bool,
) -> Iterator[str]:
    for line in lines:
        stripped = line.rstrip("\n")

        if pattern is not None:
            matched = matches_pattern(stripped, pattern)
            if invert and matched:
                continue
            if not invert and not matched:
                continue

        if start is not None or end is not None:
            ts = extract_timestamp(stripped)
            if ts is not None:
                if start is not None and ts < start:
                    continue
                if end is not None and ts > end:
                    continue

        yield line
