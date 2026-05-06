"""Statistics collection for log processing runs."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LogStats:
    total_lines: int = 0
    matched_lines: int = 0
    skipped_lines: int = 0
    parse_errors: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    earliest_entry: Optional[datetime] = None
    latest_entry: Optional[datetime] = None

    def record_line(self, matched: bool, timestamp: Optional[datetime] = None) -> None:
        self.total_lines += 1
        if matched:
            self.matched_lines += 1
            if timestamp:
                if self.earliest_entry is None or timestamp < self.earliest_entry:
                    self.earliest_entry = timestamp
                if self.latest_entry is None or timestamp > self.latest_entry:
                    self.latest_entry = timestamp
        else:
            self.skipped_lines += 1

    def record_error(self) -> None:
        self.parse_errors += 1
        self.total_lines += 1
        self.skipped_lines += 1

    @property
    def elapsed_seconds(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def match_rate(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.matched_lines / self.total_lines

    def to_dict(self) -> dict:
        return {
            "total_lines": self.total_lines,
            "matched_lines": self.matched_lines,
            "skipped_lines": self.skipped_lines,
            "parse_errors": self.parse_errors,
            "match_rate": round(self.match_rate, 4),
            "elapsed_seconds": self.elapsed_seconds,
            "earliest_entry": self.earliest_entry.isoformat() if self.earliest_entry else None,
            "latest_entry": self.latest_entry.isoformat() if self.latest_entry else None,
        }
