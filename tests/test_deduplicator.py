"""Tests for logslice.deduplicator."""

from __future__ import annotations

import pytest

from logslice.deduplicator import deduplicate


def collect(lines):
    return list(deduplicate(lines))


# ---------------------------------------------------------------------------
# Exact deduplication
# ---------------------------------------------------------------------------

class TestExactDedup:
    def test_empty_input_yields_nothing(self):
        assert collect([]) == []

    def test_single_line_passes_through(self):
        result = collect(["hello\n"])
        assert result == ["hello\n"]

    def test_duplicate_lines_removed(self):
        lines = ["error: disk full\n"] * 5
        result = collect(lines)
        assert result == ["error: disk full\n"]

    def test_unique_lines_all_kept(self):
        lines = ["line one\n", "line two\n", "line three\n"]
        result = collect(lines)
        assert result == lines

    def test_order_of_first_occurrence_preserved(self):
        lines = ["b\n", "a\n", "b\n", "c\n", "a\n"]
        result = collect(lines)
        assert result == ["b\n", "a\n", "c\n"]

    def test_lines_without_newline_normalised(self):
        lines = ["no newline", "no newline"]
        result = collect(lines)
        assert len(result) == 1
        assert result[0] == "no newline\n"


# ---------------------------------------------------------------------------
# Fuzzy deduplication
# ---------------------------------------------------------------------------

class TestFuzzyDedup:
    def _collect(self, lines, **kw):
        return list(deduplicate(lines, fuzzy=True, **kw))

    def test_same_message_different_timestamps_deduplicated(self):
        lines = [
            "2024-01-01 10:00:00 ERROR connection refused\n",
            "2024-01-01 10:00:05 ERROR connection refused\n",
            "2024-01-02T08:30:00Z ERROR connection refused\n",
        ]
        result = self._collect(lines)
        assert len(result) == 1

    def test_different_messages_kept_separate(self):
        lines = [
            "2024-01-01 10:00:00 ERROR disk full\n",
            "2024-01-01 10:00:01 ERROR out of memory\n",
        ]
        result = self._collect(lines)
        assert len(result) == 2

    def test_first_occurrence_text_is_kept(self):
        lines = [
            "2024-01-01 10:00:00 WARN retrying attempt 1\n",
            "2024-01-01 10:00:01 WARN retrying attempt 2\n",
        ]
        result = self._collect(lines)
        assert len(result) == 1
        assert "10:00:00" in result[0]


# ---------------------------------------------------------------------------
# Count mode
# ---------------------------------------------------------------------------

class TestCountMode:
    def test_count_appended_when_duplicates_exist(self):
        lines = ["oops\n"] * 4
        result = list(deduplicate(lines, count=True))
        assert result == ["oops (x4)\n"]

    def test_no_count_suffix_for_unique_lines(self):
        result = list(deduplicate(["unique\n"], count=True))
        assert result == ["unique\n"]

    def test_count_with_fuzzy(self):
        lines = [
            "2024-01-01 10:00:00 ERROR boom\n",
            "2024-01-01 10:00:01 ERROR boom\n",
            "2024-01-01 10:00:02 ERROR boom\n",
        ]
        result = list(deduplicate(lines, fuzzy=True, count=True))
        assert len(result) == 1
        assert "(x3)" in result[0]
