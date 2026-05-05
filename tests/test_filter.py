"""Tests for logslice.filter module."""

from datetime import datetime

import pytest

from logslice.filter import filter_lines

SAMPLE_LINES = [
    "2024-03-15T08:00:00 INFO  server started\n",
    "2024-03-15T09:30:00 ERROR disk usage at 90%\n",
    "2024-03-15T10:00:00 WARN  memory pressure\n",
    "2024-03-15T11:00:00 ERROR connection refused\n",
    "2024-03-15T12:00:00 INFO  backup complete\n",
]


def collect(lines, **kwargs):
    return list(filter_lines(lines, **kwargs))


class TestPatternFilter:
    def test_filter_by_pattern(self):
        result = collect(SAMPLE_LINES, pattern=r"ERROR")
        assert len(result) == 2
        assert all("ERROR" in r for r in result)

    def test_no_match_returns_empty(self):
        result = collect(SAMPLE_LINES, pattern=r"CRITICAL")
        assert result == []

    def test_no_pattern_returns_all(self):
        result = collect(SAMPLE_LINES)
        assert len(result) == 5

    def test_ignore_case(self):
        result = collect(SAMPLE_LINES, pattern=r"error", ignore_case=True)
        assert len(result) == 2

    def test_invalid_pattern_raises(self):
        with pytest.raises(ValueError):
            collect(SAMPLE_LINES, pattern=r"[bad")


class TestTimeRangeFilter:
    def test_start_filter(self):
        start = datetime(2024, 3, 15, 10, 0, 0)
        result = collect(SAMPLE_LINES, start=start)
        assert len(result) == 3

    def test_end_filter(self):
        end = datetime(2024, 3, 15, 9, 30, 0)
        result = collect(SAMPLE_LINES, end=end)
        assert len(result) == 2

    def test_start_and_end(self):
        start = datetime(2024, 3, 15, 9, 0, 0)
        end = datetime(2024, 3, 15, 11, 0, 0)
        result = collect(SAMPLE_LINES, start=start, end=end)
        assert len(result) == 3

    def test_combined_pattern_and_time(self):
        start = datetime(2024, 3, 15, 9, 0, 0)
        result = collect(SAMPLE_LINES, pattern=r"ERROR", start=start)
        assert len(result) == 2


class TestEdgeCases:
    def test_empty_lines_skipped(self):
        lines = ["\n", "   \n", "2024-03-15T08:00:00 INFO hello\n"]
        result = collect(lines)
        assert len(result) == 1

    def test_lines_without_timestamp_pass_time_filter(self):
        lines = ["no timestamp line\n"]
        start = datetime(2024, 1, 1)
        result = collect(lines, start=start)
        # Lines without timestamps are not filtered out by time range
        assert len(result) == 1
