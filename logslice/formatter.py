"""Output formatting utilities for logslice."""

import json
from datetime import datetime
from typing import Optional


DEFAULT_FORMAT = "plain"
SUPPORTED_FORMATS = ("plain", "json", "csv")


def format_line(line: str, fmt: str = DEFAULT_FORMAT, line_number: Optional[int] = None) -> str:
    """Format a single log line according to the requested output format."""
    line = line.rstrip("\n")

    if fmt == "plain":
        if line_number is not None:
            return f"{line_number}: {line}"
        return line

    if fmt == "json":
        record = {"line": line}
        if line_number is not None:
            record["n"] = line_number
        return json.dumps(record)

    if fmt == "csv":
        escaped = line.replace('"', '""')
        if line_number is not None:
            return f'{line_number},"{escaped}"'
        return f'"{escaped}"'

    raise ValueError(f"Unsupported format: {fmt!r}. Choose from {SUPPORTED_FORMATS}")


def format_header(fmt: str) -> Optional[str]:
    """Return a header row for formats that need one (e.g. CSV)."""
    if fmt == "csv":
        return 'n,"line"'
    return None


def format_summary(matched: int, total: int, fmt: str = DEFAULT_FORMAT) -> str:
    """Return a summary string after processing."""
    if fmt == "json":
        return json.dumps({"matched": matched, "total": total})
    if fmt == "csv":
        return f'# matched={matched} total={total}'
    return f"# matched {matched}/{total} lines"
