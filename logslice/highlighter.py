"""Highlight regex pattern matches within log lines."""

import re
from typing import Optional

ANSI_RESET = "\033[0m"
ANSI_BOLD_RED = "\033[1;31m"
ANSI_BOLD_YELLOW = "\033[1;33m"
ANSI_BOLD_GREEN = "\033[1;32m"

COLOR_MAP = {
    "red": ANSI_BOLD_RED,
    "yellow": ANSI_BOLD_YELLOW,
    "green": ANSI_BOLD_GREEN,
}


def highlight_match(line: str, pattern: str, color: str = "red") -> str:
    """Wrap every occurrence of pattern in ANSI color codes.

    Args:
        line: The raw log line text.
        pattern: Regex pattern whose matches should be highlighted.
        color: One of 'red', 'yellow', 'green'. Defaults to 'red'.

    Returns:
        The line with matching spans wrapped in ANSI escape sequences.
        Returns the original line unchanged if pattern is empty.
    """
    if not pattern:
        return line

    ansi = COLOR_MAP.get(color, ANSI_BOLD_RED)

    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        return f"{ansi}{m.group(0)}{ANSI_RESET}"

    try:
        return re.sub(pattern, _replace, line)
    except re.error:
        return line


def strip_ansi(text: str) -> str:
    """Remove all ANSI escape sequences from *text*."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def highlight_lines(
    lines: "list[str]",
    pattern: Optional[str],
    color: str = "red",
) -> "list[str]":
    """Apply :func:`highlight_match` to every line in *lines*.

    Lines are returned unchanged when *pattern* is ``None`` or empty.
    """
    if not pattern:
        return lines
    return [highlight_match(line, pattern, color) for line in lines]
