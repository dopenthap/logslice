"""Tests for logslice.aggregator."""

from __future__ import annotations

import pytest

from logslice.aggregator import (
    aggregate_by,
    count_by,
    iter_aggregated,
    top_keys,
)


def _first_word(line: str) -> str | None:
    parts = line.split()
    return parts[0] if parts else None


# ---------------------------------------------------------------------------
# aggregate_by
# ---------------------------------------------------------------------------

class TestAggregateBy:
    def test_empty_input_returns_empty_dict(self):
        assert aggregate_by([], _first_word) == {}

    def test_single_line_single_bucket(self):
        result = aggregate_by(["ERROR something"], _first_word)
        assert result == {"ERROR": ["ERROR something"]}

    def test_groups_multiple_lines(self):
        lines = ["ERROR a", "INFO b", "ERROR c"]
        result = aggregate_by(lines, _first_word)
        assert result["ERROR"] == ["ERROR a", "ERROR c"]
        assert result["INFO"] == ["INFO b"]

    def test_none_key_goes_to_unkeyed(self):
        result = aggregate_by(["", "INFO x"], _first_word)
        assert "__unkeyed__" in result
        assert "" in result["__unkeyed__"]

    def test_preserves_insertion_order_within_bucket(self):
        lines = ["A 1", "A 2", "A 3"]
        result = aggregate_by(lines, _first_word)
        assert result["A"] == ["A 1", "A 2", "A 3"]


# ---------------------------------------------------------------------------
# count_by
# ---------------------------------------------------------------------------

class TestCountBy:
    def test_empty_input_returns_empty(self):
        assert count_by([], _first_word) == {}

    def test_counts_correctly(self):
        lines = ["ERROR a", "ERROR b", "INFO c"]
        result = count_by(lines, _first_word)
        assert result["ERROR"] == 2
        assert result["INFO"] == 1

    def test_none_key_counted_under_unkeyed(self):
        result = count_by(["", ""], _first_word)
        assert result["__unkeyed__"] == 2


# ---------------------------------------------------------------------------
# iter_aggregated
# ---------------------------------------------------------------------------

class TestIterAggregated:
    def test_yields_all_buckets(self):
        buckets = {"A": ["A 1"], "B": ["B 1", "B 2"]}
        pairs = list(iter_aggregated(buckets))
        assert len(pairs) == 2

    def test_sort_keys_orders_output(self):
        buckets = {"Z": [], "A": [], "M": []}
        keys = [k for k, _ in iter_aggregated(buckets, sort_keys=True)]
        assert keys == ["A", "M", "Z"]

    def test_no_sort_preserves_dict_order(self):
        buckets = {"Z": [], "A": [], "M": []}
        keys = [k for k, _ in iter_aggregated(buckets, sort_keys=False)]
        assert keys == ["Z", "A", "M"]


# ---------------------------------------------------------------------------
# top_keys
# ---------------------------------------------------------------------------

class TestTopKeys:
    def test_returns_top_n(self):
        counts = {"A": 5, "B": 3, "C": 8, "D": 1}
        result = top_keys(counts, n=2)
        assert result == [("C", 8), ("A", 5)]

    def test_n_larger_than_dict_returns_all(self):
        counts = {"A": 1, "B": 2}
        assert len(top_keys(counts, n=100)) == 2

    def test_empty_counts_returns_empty(self):
        assert top_keys({}) == []
