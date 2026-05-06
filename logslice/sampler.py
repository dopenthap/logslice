"""Line sampling utilities for large log files."""

import random
from typing import Iterable, Iterator


def sample_lines(
    lines: Iterable[str],
    rate: float,
    seed: int | None = None,
) -> Iterator[str]:
    """Yield lines randomly sampled at the given rate (0.0–1.0).

    Args:
        lines: Input iterable of log lines.
        rate: Fraction of lines to keep, e.g. 0.1 for 10%.
        seed: Optional RNG seed for reproducibility.

    Yields:
        Sampled lines.

    Raises:
        ValueError: If rate is not in the range [0.0, 1.0].
    """
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"Sample rate must be between 0.0 and 1.0, got {rate}")

    rng = random.Random(seed)

    for line in lines:
        if rng.random() < rate:
            yield line


def sample_every_nth(lines: Iterable[str], n: int) -> Iterator[str]:
    """Yield every nth line from the input.

    Args:
        lines: Input iterable of log lines.
        n: Step size; must be >= 1.

    Yields:
        Every nth line (1-indexed).

    Raises:
        ValueError: If n is less than 1.
    """
    if n < 1:
        raise ValueError(f"Step n must be >= 1, got {n}")

    for i, line in enumerate(lines):
        if i % n == 0:
            yield line
