"""Per-window statistics helpers."""

from dataclasses import dataclass, field
from typing import Callable, Generator, Iterable, List, Optional

from logslice.window import tumbling_window, sliding_window


@dataclass
class WindowSummary:
    index: int
    size: int
    matched: int
    lines: List[str]

    @property
    def match_rate(self) -> float:
        return self.matched / self.size if self.size else 0.0


def summarize_windows(
    lines: Iterable[str],
    window_size: int,
    predicate: Callable[[str], bool],
    *,
    sliding: bool = False,
    step: int = 1,
) -> Generator[WindowSummary, None, None]:
    """Yield a WindowSummary for each window.

    Parameters
    ----------
    lines:       source lines
    window_size: number of lines per window
    predicate:   function that returns True for a line of interest
    sliding:     use sliding windows instead of tumbling
    step:        advance step for sliding windows
    """
    windower = (
        sliding_window(lines, window_size, step=step)
        if sliding
        else tumbling_window(lines, window_size)
    )
    for idx, window in enumerate(windower):
        matched = sum(1 for ln in window if predicate(ln))
        yield WindowSummary(
            index=idx,
            size=len(window),
            matched=matched,
            lines=window,
        )


def windows_above_threshold(
    summaries: Iterable[WindowSummary],
    threshold: float,
) -> Generator[WindowSummary, None, None]:
    """Yield only windows whose match_rate meets or exceeds *threshold*."""
    for summary in summaries:
        if summary.match_rate >= threshold:
            yield summary
