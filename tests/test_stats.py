"""Tests for logslice.stats module."""

from datetime import datetime

import pytest

from logslice.stats import LogStats


DT1 = datetime(2024, 1, 10, 8, 0, 0)
DT2 = datetime(2024, 1, 10, 9, 30, 0)
DT3 = datetime(2024, 1, 10, 7, 15, 0)


def make_stats() -> LogStats:
    return LogStats()


class TestRecordLine:
    def test_matched_increments_counts(self):
        s = make_stats()
        s.record_line(matched=True)
        assert s.total_lines == 1
        assert s.matched_lines == 1
        assert s.skipped_lines == 0

    def test_unmatched_increments_skipped(self):
        s = make_stats()
        s.record_line(matched=False)
        assert s.total_lines == 1
        assert s.skipped_lines == 1
        assert s.matched_lines == 0

    def test_timestamp_tracking(self):
        s = make_stats()
        s.record_line(matched=True, timestamp=DT2)
        s.record_line(matched=True, timestamp=DT1)
        s.record_line(matched=True, timestamp=DT3)
        assert s.earliest_entry == DT3
        assert s.latest_entry == DT2

    def test_unmatched_does_not_track_timestamp(self):
        s = make_stats()
        s.record_line(matched=False, timestamp=DT1)
        assert s.earliest_entry is None
        assert s.latest_entry is None


class TestRecordError:
    def test_increments_errors_and_skipped(self):
        s = make_stats()
        s.record_error()
        assert s.parse_errors == 1
        assert s.skipped_lines == 1
        assert s.total_lines == 1


class TestMatchRate:
    def test_zero_when_no_lines(self):
        s = make_stats()
        assert s.match_rate == 0.0

    def test_correct_rate(self):
        s = make_stats()
        for _ in range(3):
            s.record_line(matched=True)
        for _ in range(7):
            s.record_line(matched=False)
        assert s.match_rate == pytest.approx(0.3)


class TestElapsed:
    def test_none_when_times_missing(self):
        s = make_stats()
        assert s.elapsed_seconds is None

    def test_calculates_elapsed(self):
        s = make_stats()
        s.start_time = datetime(2024, 1, 1, 0, 0, 0)
        s.end_time = datetime(2024, 1, 1, 0, 0, 5)
        assert s.elapsed_seconds == pytest.approx(5.0)


class TestToDict:
    def test_keys_present(self):
        s = make_stats()
        d = s.to_dict()
        expected_keys = {
            "total_lines", "matched_lines", "skipped_lines",
            "parse_errors", "match_rate", "elapsed_seconds",
            "earliest_entry", "latest_entry",
        }
        assert expected_keys == set(d.keys())
