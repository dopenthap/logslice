"""Core log line parsing: regex matching and timestamp extraction."""

import re
from datetime import datetime
from typing import Optional

# Common timestamp formats found in log files
TIMESTAMP_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%d/%b/%Y:%H:%M:%S",
    "%b %d %H:%M:%S",
]

TIMESTAMP_PATTERNS = [
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
    r"(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})",
    r"(\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2})",
]


def extract_timestamp(line: str) -> Optional[datetime]:
    """Try to extract a datetime from a log line using known patterns."""
    for pattern, fmt in zip(TIMESTAMP_PATTERNS, TIMESTAMP_FORMATS):
        match = re.search(pattern, line)
        if match:
            raw = match.group(1)
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
    return None


def matches_pattern(line: str, pattern: str, ignore_case: bool = False) -> bool:
    """Return True if the line matches the given regex pattern."""
    flags = re.IGNORECASE if ignore_case else 0
    try:
        return bool(re.search(pattern, line, flags))
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern '{pattern}': {exc}") from exc


def parse_line(line: str) -> dict:
    """Parse a log line into a dict with raw text and extracted timestamp."""
    return {
        "raw": line.rstrip("\n"),
        "timestamp": extract_timestamp(line),
    }
