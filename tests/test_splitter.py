"""Tests for logslice.splitter."""

import io
import pytest
from logslice.splitter import split_to_streams, split_to_buffers


def is_error(line: str) -> bool:
    return "ERROR" in line


def is_warn(line: str) -> bool:
    return "WARN" in line


ROUTES = [("error", is_error), ("warn", is_warn)]

LINES = [
    "2024-01-01 ERROR broke\n",
    "2024-01-01 WARN disk low\n",
    "2024-01-01 INFO ok\n",
    "2024-01-01 ERROR again\n",
]


class TestSplitToStreams:
    def _make_streams(self, keys):
        return {k: io.StringIO() for k in keys}

    def test_routes_lines_to_correct_streams(self):
        streams = self._make_streams(["error", "warn"])
        split_to_streams(LINES, ROUTES, streams)
        streams["error"].seek(0)
        content = streams["error"].read()
        assert "ERROR broke" in content
        assert "ERROR again" in content

    def test_warn_stream_receives_warn_lines(self):
        streams = self._make_streams(["error", "warn"])
        split_to_streams(LINES, ROUTES, streams)
        streams["warn"].seek(0)
        assert "WARN disk low" in streams["warn"].read()

    def test_unmatched_dropped_without_default(self):
        streams = self._make_streams(["error", "warn"])
        counts = split_to_streams(LINES, ROUTES, streams)
        assert counts.get("other", 0) == 0

    def test_unmatched_goes_to_default_stream(self):
        streams = self._make_streams(["error", "warn", "other"])
        counts = split_to_streams(LINES, ROUTES, streams, default_key="other")
        assert counts["other"] == 1

    def test_counts_match_lines_written(self):
        streams = self._make_streams(["error", "warn"])
        counts = split_to_streams(LINES, ROUTES, streams)
        assert counts["error"] == 2
        assert counts["warn"] == 1

    def test_lines_get_newline_appended_if_missing(self):
        streams = self._make_streams(["error"])
        split_to_streams(["ERROR no newline"], ROUTES, streams)
        streams["error"].seek(0)
        assert streams["error"].read().endswith("\n")

    def test_empty_input_writes_nothing(self):
        streams = self._make_streams(["error", "warn"])
        counts = split_to_streams([], ROUTES, streams)
        assert all(v == 0 for v in counts.values())


class TestSplitToBuffers:
    def test_returns_buffers_and_counts(self):
        buffers, counts = split_to_buffers(LINES, ROUTES)
        assert "error" in buffers
        assert "warn" in buffers
        assert counts["error"] == 2

    def test_buffers_are_rewound(self):
        buffers, _ = split_to_buffers(LINES, ROUTES)
        content = buffers["error"].read()
        assert len(content) > 0

    def test_default_key_captures_unmatched(self):
        buffers, counts = split_to_buffers(LINES, ROUTES, default_key="other")
        assert "other" in buffers
        assert counts["other"] == 1

    def test_empty_input_returns_empty_dicts(self):
        buffers, counts = split_to_buffers([], ROUTES)
        assert buffers == {}
        assert counts == {}
