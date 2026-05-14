"""Tag log lines with labels based on regex rules."""

from __future__ import annotations

import re
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple

TagRule = Tuple[str, re.Pattern]


def compile_rules(rules: Dict[str, str]) -> List[TagRule]:
    """Compile a mapping of {label: pattern_str} into (label, pattern) pairs."""
    compiled: List[TagRule] = []
    for label, pattern in rules.items():
        compiled.append((label, re.compile(pattern)))
    return compiled


def tag_line(line: str, rules: List[TagRule]) -> Optional[str]:
    """Return the first matching tag label for *line*, or None."""
    for label, pattern in rules:
        if pattern.search(line):
            return label
    return None


def tag_all(line: str, rules: List[TagRule]) -> List[str]:
    """Return every matching tag label for *line* (may be empty)."""
    return [label for label, pattern in rules if pattern.search(line)]


def tag_lines(
    lines: Iterable[str],
    rules: List[TagRule],
    *,
    multi: bool = False,
    prefix: str = "[{tag}] ",
) -> Iterator[str]:
    """Yield lines prepended with their tag(s).

    If *multi* is False (default) only the first matching tag is prepended.
    Lines with no matching tag are yielded unchanged.
    """
    for line in lines:
        stripped = line.rstrip("\n")
        nl = "\n" if line.endswith("\n") else ""
        if multi:
            tags = tag_all(stripped, rules)
            if tags:
                label = ",".join(tags)
                yield prefix.format(tag=label) + stripped + nl
            else:
                yield line
        else:
            label = tag_line(stripped, rules)
            if label is not None:
                yield prefix.format(tag=label) + stripped + nl
            else:
                yield line


def filter_by_tag(
    lines: Iterable[str],
    rules: List[TagRule],
    wanted: str,
) -> Iterator[str]:
    """Yield only lines whose first tag matches *wanted*."""
    for line in lines:
        if tag_line(line.rstrip("\n"), rules) == wanted:
            yield line
