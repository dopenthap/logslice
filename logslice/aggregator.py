"""Aggregate log lines by a key, counting occurrences or collecting values."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, Iterator, List, Tuple


AggregateResult = Dict[str, List[str]]


def aggregate_by(
    lines: Iterable[str],
    key_fn: Callable[[str], str | None],
) -> AggregateResult:
    """Group lines by the value returned by *key_fn*.

    Lines for which *key_fn* returns ``None`` are placed under the
    ``"__unkeyed__"`` bucket so they are never silently dropped.
    """
    buckets: AggregateResult = defaultdict(list)
    for line in lines:
        key = key_fn(line)
        if key is None:
            key = "__unkeyed__"
        buckets[key].append(line)
    return dict(buckets)


def count_by(
    lines: Iterable[str],
    key_fn: Callable[[str], str | None],
) -> Dict[str, int]:
    """Return a mapping of key → occurrence count."""
    counts: Dict[str, int] = defaultdict(int)
    for line in lines:
        key = key_fn(line) or "__unkeyed__"
        counts[key] += 1
    return dict(counts)


def iter_aggregated(
    buckets: AggregateResult,
    *,
    sort_keys: bool = False,
) -> Iterator[Tuple[str, List[str]]]:
    """Yield ``(key, lines)`` pairs, optionally sorted by key."""
    keys = sorted(buckets) if sort_keys else list(buckets)
    for key in keys:
        yield key, buckets[key]


def top_keys(
    counts: Dict[str, int],
    n: int = 10,
) -> List[Tuple[str, int]]:
    """Return the *n* most common keys as ``(key, count)`` pairs."""
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:n]
