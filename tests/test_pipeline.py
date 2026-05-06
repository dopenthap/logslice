"""Tests for the pipeline module."""

import io
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from logslice.pipeline import _iter_with_stats, _matches, run_pipeline
from logslice.stats import LogStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_stream(*lines):
    """Return a StringIO stream containing the given lines."""
    return io.StringIO("\n".join(lines) + ("\n" if lines else ""))


def make_stats():
    return LogStats(start=datetime.now(timezone.utc))


def collect(gen):
    return list(gen)


# ---------------------------------------------------------------------------
# _matches
# ---------------------------------------------------------------------------

class TestMatches:
    def test_no_filters_always_true(self):
        assert _matches("anything", pattern=None, start=None, end=None) is True

    def test_pattern_match(self):
        assert _matches("ERROR: disk full", pattern="ERROR", start=None, end=None) is True

    def test_pattern_no_match(self):
        assert _matches("INFO: all good", pattern="ERROR", start=None, end=None) is False

    def test_start_filter_passes_when_no_timestamp(self):
        # Lines without timestamps pass through time filters unchanged
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert _matches("no timestamp here", pattern=None, start=start, end=None) is True

    def test_start_filter_excludes_old_line(self):
        start = datetime(2024, 6, 1, tzinfo=timezone.utc)
        line = "2024-01-15T10:00:00Z INFO old event"
        assert _matches(line, pattern=None, start=start, end=None) is False

    def test_end_filter_excludes_future_line(self):
        end = datetime(2024, 1, 1, tzinfo=timezone.utc)
        line = "2024-06-15T10:00:00Z INFO future event"
        assert _matches(line, pattern=None, start=None, end=end) is False

    def test_both_filters_within_range(self):
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 12, 31, tzinfo=timezone.utc)
        line = "2024-06-15T10:00:00Z INFO mid-year event"
        assert _matches(line, pattern=None, start=start, end=end) is True

    def test_pattern_and_time_both_must_match(self):
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        line = "2024-06-15T10:00:00Z INFO some event"
        # pattern doesn't match even though time is fine
        assert _matches(line, pattern="ERROR", start=start, end=None) is False


# ---------------------------------------------------------------------------
# _iter_with_stats
# ---------------------------------------------------------------------------

class TestIterWithStats:
    def test_yields_matched_lines(self):
        stats = make_stats()
        stream = make_stream("line one", "line two")
        results = collect(_iter_with_stats(stream, stats, pattern=None, start=None, end=None))
        assert results == ["line one\n", "line two\n"]

    def test_records_total_and_matched(self):
        stats = make_stats()
        stream = make_stream("ERROR: bad", "INFO: ok")
        collect(_iter_with_stats(stream, stats, pattern="ERROR", start=None, end=None))
        assert stats.total_lines == 2
        assert stats.matched_lines == 1
        assert stats.skipped_lines == 1

    def test_empty_stream_no_lines(self):
        stats = make_stats()
        stream = io.StringIO("")
        results = collect(_iter_with_stats(stream, stats, pattern=None, start=None, end=None))
        assert results == []
        assert stats.total_lines == 0

    def test_all_filtered_out(self):
        stats = make_stats()
        stream = make_stream("INFO: a", "INFO: b", "INFO: c")
        results = collect(_iter_with_stats(stream, stats, pattern="ERROR", start=None, end=None))
        assert results == []
        assert stats.skipped_lines == 3


# ---------------------------------------------------------------------------
# run_pipeline
# ---------------------------------------------------------------------------

class TestRunPipeline:
    def test_basic_run_returns_stats(self):
        stream = make_stream("hello world", "goodbye world")
        out = io.StringIO()
        stats = run_pipeline(
            source=stream,
            output=out,
            pattern=None,
            start=None,
            end=None,
            fmt="plain",
            sample_rate=1.0,
        )
        assert stats.total_lines == 2
        assert stats.matched_lines == 2

    def test_pattern_filters_output(self):
        stream = make_stream("ERROR: oops", "INFO: fine", "ERROR: again")
        out = io.StringIO()
        stats = run_pipeline(
            source=stream,
            output=out,
            pattern="ERROR",
            start=None,
            end=None,
            fmt="plain",
            sample_rate=1.0,
        )
        assert stats.matched_lines == 2
        assert stats.skipped_lines == 1
        written = out.getvalue()
        assert "ERROR: oops" in written
        assert "INFO: fine" not in written

    def test_sample_rate_zero_matches_nothing(self):
        stream = make_stream("line 1", "line 2", "line 3")
        out = io.StringIO()
        stats = run_pipeline(
            source=stream,
            output=out,
            pattern=None,
            start=None,
            end=None,
            fmt="plain",
            sample_rate=0.0,
        )
        assert out.getvalue() == ""

    def test_json_format_produces_json_lines(self):
        stream = make_stream("some log line")
        out = io.StringIO()
        run_pipeline(
            source=stream,
            output=out,
            pattern=None,
            start=None,
            end=None,
            fmt="json",
            sample_rate=1.0,
        )
        import json
        line = out.getvalue().strip()
        parsed = json.loads(line)
        assert "line" in parsed
