"""Tests for logslice.reporter module."""

import io
import json
from datetime import datetime

from logslice.stats import LogStats
from logslice.reporter import format_stats_plain, format_stats_json, write_stats


def make_populated_stats() -> LogStats:
    s = LogStats()
    s.start_time = datetime(2024, 3, 1, 10, 0, 0)
    s.end_time = datetime(2024, 3, 1, 10, 0, 2)
    s.record_line(matched=True, timestamp=datetime(2024, 3, 1, 9, 0, 0))
    s.record_line(matched=True, timestamp=datetime(2024, 3, 1, 9, 30, 0))
    s.record_line(matched=False)
    s.record_error()
    return s


class TestFormatStatsPlain:
    def test_contains_totals(self):
        s = make_populated_stats()
        out = format_stats_plain(s)
        assert "Total lines   : 4" in out
        assert "Matched lines : 2" in out
        assert "Skipped lines : 2" in out

    def test_contains_elapsed(self):
        s = make_populated_stats()
        out = format_stats_plain(s)
        assert "Elapsed" in out
        assert "2.000s" in out

    def test_contains_timestamps(self):
        s = make_populated_stats()
        out = format_stats_plain(s)
        assert "Earliest entry" in out
        assert "Latest entry" in out

    def test_no_elapsed_when_times_missing(self):
        s = LogStats()
        out = format_stats_plain(s)
        assert "Elapsed" not in out


class TestFormatStatsJson:
    def test_valid_json(self):
        s = make_populated_stats()
        out = format_stats_json(s)
        data = json.loads(out)
        assert data["total_lines"] == 4
        assert data["matched_lines"] == 2
        assert data["parse_errors"] == 1

    def test_match_rate_rounded(self):
        s = make_populated_stats()
        data = json.loads(format_stats_json(s))
        assert isinstance(data["match_rate"], float)


class TestWriteStats:
    def test_plain_writes_to_stream(self):
        s = make_populated_stats()
        buf = io.StringIO()
        write_stats(s, buf, fmt="plain")
        assert "logslice summary" in buf.getvalue()

    def test_json_writes_to_stream(self):
        s = make_populated_stats()
        buf = io.StringIO()
        write_stats(s, buf, fmt="json")
        data = json.loads(buf.getvalue())
        assert "total_lines" in data

    def test_default_format_is_plain(self):
        s = LogStats()
        buf = io.StringIO()
        write_stats(s, buf)
        assert "logslice summary" in buf.getvalue()
