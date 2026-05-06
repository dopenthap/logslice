"""Human-readable and JSON reporting for log stats."""

import json
from typing import IO

from logslice.stats import LogStats


def format_stats_plain(stats: LogStats) -> str:
    lines = [
        "--- logslice summary ---",
        f"  Total lines   : {stats.total_lines}",
        f"  Matched lines : {stats.matched_lines}",
        f"  Skipped lines : {stats.skipped_lines}",
        f"  Parse errors  : {stats.parse_errors}",
        f"  Match rate    : {stats.match_rate:.1%}",
    ]
    if stats.elapsed_seconds is not None:
        lines.append(f"  Elapsed       : {stats.elapsed_seconds:.3f}s")
    if stats.earliest_entry:
        lines.append(f"  Earliest entry: {stats.earliest_entry.isoformat()}")
    if stats.latest_entry:
        lines.append(f"  Latest entry  : {stats.latest_entry.isoformat()}")
    lines.append("------------------------")
    return "\n".join(lines)


def format_stats_json(stats: LogStats) -> str:
    return json.dumps(stats.to_dict(), indent=2)


def write_stats(stats: LogStats, stream: IO[str], fmt: str = "plain") -> None:
    """Write stats report to the given stream."""
    if fmt == "json":
        stream.write(format_stats_json(stats) + "\n")
    else:
        stream.write(format_stats_plain(stats) + "\n")
