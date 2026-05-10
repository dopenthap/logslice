"""Route log lines to different outputs based on predicate functions."""

from typing import Callable, Dict, Generator, Iterable, List, Optional, Tuple

Predicate = Callable[[str], bool]
Route = Tuple[str, Predicate]


def make_router(routes: List[Route], default_key: Optional[str] = None):
    """Return a function that maps a line to the first matching route key.

    Args:
        routes: ordered list of (key, predicate) pairs.
        default_key: key to use when no route matches; None drops the line.

    Returns:
        A callable (line -> Optional[str]).
    """
    def _route(line: str) -> Optional[str]:
        for key, pred in routes:
            if pred(line):
                return key
        return default_key

    return _route


def route_lines(
    lines: Iterable[str],
    routes: List[Route],
    default_key: Optional[str] = None,
) -> Dict[str, List[str]]:
    """Partition *lines* into buckets according to *routes*.

    Lines that match no route are placed under *default_key* (if given) or
    silently dropped.

    Returns:
        A dict mapping each key that received at least one line to its lines.
    """
    router = make_router(routes, default_key)
    buckets: Dict[str, List[str]] = {}
    for line in lines:
        key = router(line)
        if key is not None:
            buckets.setdefault(key, []).append(line)
    return buckets


def iter_routed(
    lines: Iterable[str],
    routes: List[Route],
    default_key: Optional[str] = None,
) -> Generator[Tuple[str, str], None, None]:
    """Yield (key, line) pairs for each line that matches a route.

    Lines with no matching route and no *default_key* are skipped.
    """
    router = make_router(routes, default_key)
    for line in lines:
        key = router(line)
        if key is not None:
            yield key, line
