"""Summarise tag frequency across a stream of lines."""

from __future__ import annotations

import json
from collections import Counter
from typing import Dict, Iterable, List, TextIO

from logslice.tagger import TagRule, tag_all, tag_line


def count_tags(
    lines: Iterable[str],
    rules: List[TagRule],
    *,
    multi: bool = False,
) -> Counter:
    """Count how many lines carry each tag.

    With *multi=False* each line contributes at most one count.
    With *multi=True* a line may increment several tag counters.
    """
    counts: Counter = Counter()
    for line in lines:
        stripped = line.rstrip("\n")
        if multi:
            for label in tag_all(stripped, rules):
                counts[label] += 1
        else:
            label = tag_line(stripped, rules)
            if label is not None:
                counts[label] += 1
    return counts


def format_tag_report_plain(counts: Counter) -> str:
    """Return a human-readable tag frequency report."""
    if not counts:
        return "no tags matched\n"
    total = sum(counts.values())
    lines = ["tag counts:", "-" * 20]
    for label, n in counts.most_common():
        pct = 100.0 * n / total if total else 0.0
        lines.append(f"  {label:<16} {n:>6}  ({pct:.1f}%)")
    lines.append("-" * 20)
    lines.append(f"  {'total':<16} {total:>6}")
    return "\n".join(lines) + "\n"


def format_tag_report_json(counts: Counter) -> str:
    """Return a JSON tag frequency report."""
    total = sum(counts.values())
    payload = {
        "total": total,
        "tags": {label: n for label, n in counts.most_common()},
    }
    return json.dumps(payload)


def write_tag_report(
    counts: Counter,
    out: TextIO,
    *,
    fmt: str = "plain",
) -> None:
    """Write a tag report to *out* in *fmt* format ('plain' or 'json')."""
    if fmt == "json":
        out.write(format_tag_report_json(counts) + "\n")
    else:
        out.write(format_tag_report_plain(counts))
