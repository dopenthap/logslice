"""Tests for logslice.chunker."""

import pytest
from logslice.chunker import chunk_by_size, chunk_by_time


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect(gen):
    return list(gen)


ISO_LINES = [
    "2024-01-01T00:00:00 alpha",
    "2024-01-01T00:00:30 bravo",
    "2024-01-01T00:01:10 charlie",
    "2024-01-01T00:01:45 delta",
    "2024-01-01T00:03:00 echo",
]


# ---------------------------------------------------------------------------
# chunk_by_size
# ---------------------------------------------------------------------------

class TestChunkBySize:
    def test_empty_input_yields_nothing(self):
        assert collect(chunk_by_size([], 3)) == []

    def test_exact_multiple(self):
        lines = ["a", "b", "c", "d"]
        chunks = collect(chunk_by_size(lines, 2))
        assert chunks == [["a", "b"], ["c", "d"]]

    def test_remainder_forms_last_chunk(self):
        lines = ["a", "b", "c", "d", "e"]
        chunks = collect(chunk_by_size(lines, 2))
        assert chunks == [["a", "b"], ["c", "d"], ["e"]]

    def test_chunk_size_larger_than_input(self):
        lines = ["x", "y"]
        chunks = collect(chunk_by_size(lines, 100))
        assert chunks == [["x", "y"]]

    def test_chunk_size_one(self):
        lines = ["a", "b", "c"]
        chunks = collect(chunk_by_size(lines, 1))
        assert chunks == [["a"], ["b"], ["c"]]

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            collect(chunk_by_size(["a"], 0))


# ---------------------------------------------------------------------------
# chunk_by_time
# ---------------------------------------------------------------------------

class TestChunkByTime:
    def test_empty_input_yields_nothing(self):
        assert collect(chunk_by_time([], 60)) == []

    def test_all_within_window(self):
        # first two lines are 30 s apart — fit in 60 s window
        chunks = collect(chunk_by_time(ISO_LINES[:2], 60))
        assert len(chunks) == 1
        assert len(chunks[0]) == 2

    def test_splits_on_window_boundary(self):
        # window of 60 s: lines at 0 s, 30 s, 70 s, 105 s, 180 s
        chunks = collect(chunk_by_time(ISO_LINES, 60))
        # chunk 1: 0 s, 30 s  (both within 60 s of 0 s)
        # chunk 2: 70 s, 105 s (both within 60 s of 70 s)
        # chunk 3: 180 s
        assert len(chunks) == 3

    def test_lines_without_timestamp_stay_in_current_chunk(self):
        mixed = [
            "2024-01-01T00:00:00 start",
            "no timestamp here",
            "2024-01-01T00:00:10 end",
        ]
        chunks = collect(chunk_by_time(mixed, 60))
        assert len(chunks) == 1
        assert "no timestamp here" in chunks[0]

    def test_only_untimstamped_lines_form_single_chunk(self):
        lines = ["foo", "bar", "baz"]
        chunks = collect(chunk_by_time(lines, 30))
        assert chunks == [["foo", "bar", "baz"]]

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            collect(chunk_by_time(["a"], 0))
