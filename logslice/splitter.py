"""Split a stream of lines into named sub-streams written to separate files."""

import io
from typing import Callable, Dict, Iterable, IO, List, Optional, Tuple

from logslice.router import Route, iter_routed


def split_to_streams(
    lines: Iterable[str],
    routes: List[Route],
    streams: Dict[str, IO[str]],
    default_key: Optional[str] = None,
) -> Dict[str, int]:
    """Write each line to the stream identified by its route key.

    Args:
        lines: source lines to split.
        routes: ordered (key, predicate) pairs used to classify lines.
        streams: mapping of route key -> writable text stream.
        default_key: catch-all key; its stream must be present in *streams*.

    Returns:
        A dict mapping each key to the number of lines written.
    """
    counts: Dict[str, int] = {k: 0 for k in streams}
    for key, line in iter_routed(lines, routes, default_key):
        stream = streams.get(key)
        if stream is None:
            continue
        stream.write(line if line.endswith("\n") else line + "\n")
        counts[key] = counts.get(key, 0) + 1
    return counts


def split_to_buffers(
    lines: Iterable[str],
    routes: List[Route],
    default_key: Optional[str] = None,
) -> Tuple[Dict[str, io.StringIO], Dict[str, int]]:
    """Convenience wrapper that creates in-memory StringIO buffers automatically.

    Returns:
        (buffers, counts) where *buffers* maps each key that received at least
        one line to a rewound StringIO, and *counts* maps keys to line counts.
    """
    buffers: Dict[str, io.StringIO] = {}
    counts: Dict[str, int] = {}

    for key, line in iter_routed(lines, routes, default_key):
        if key not in buffers:
            buffers[key] = io.StringIO()
        buffers[key].write(line if line.endswith("\n") else line + "\n")
        counts[key] = counts.get(key, 0) + 1

    for buf in buffers.values():
        buf.seek(0)

    return buffers, counts
