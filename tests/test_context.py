"""Tests for logslice.context."""

import pytest

from logslice.context import collect_context, context_lines

LINES = [
    "alpha",    # 0
    "ERROR one",  # 1  match
    "beta",     # 2
    "gamma",    # 3
    "ERROR two",  # 4  match
    "delta",    # 5
]


def is_error(line: str) -> bool:
    return "ERROR" in line


class TestContextLines:
    def test_no_context_yields_only_matches(self):
        result = collect_context(LINES, predicate=is_error)
        assert [ln for ln, _ in result] == ["ERROR one", "ERROR two"]
        assert all(is_match for _, is_match in result)

    def test_before_context(self):
        result = collect_context(LINES, before=1, predicate=is_error)
        lines_only = [ln for ln, _ in result]
        assert "alpha" in lines_only      # before ERROR one
        assert "ERROR one" in lines_only
        assert "gamma" in lines_only      # before ERROR two
        assert "ERROR two" in lines_only

    def test_after_context(self):
        result = collect_context(LINES, after=1, predicate=is_error)
        lines_only = [ln for ln, _ in result]
        assert "ERROR one" in lines_only
        assert "beta" in lines_only       # after ERROR one
        assert "ERROR two" in lines_only
        assert "delta" in lines_only      # after ERROR two

    def test_before_and_after(self):
        result = collect_context(LINES, before=1, after=1, predicate=is_error)
        lines_only = [ln for ln, _ in result]
        assert "alpha" in lines_only
        assert "ERROR one" in lines_only
        assert "beta" in lines_only
        assert "gamma" in lines_only
        assert "ERROR two" in lines_only
        assert "delta" in lines_only

    def test_is_match_flag_correct(self):
        result = collect_context(LINES, before=1, predicate=is_error)
        mapping = {ln: flag for ln, flag in result}
        assert mapping["ERROR one"] is True
        assert mapping["ERROR two"] is True
        assert mapping["alpha"] is False

    def test_none_predicate_yields_all(self):
        result = collect_context(LINES)
        assert len(result) == len(LINES)
        assert all(is_match for _, is_match in result)

    def test_empty_input(self):
        assert collect_context([], predicate=is_error) == []

    def test_no_matches_yields_nothing(self):
        result = collect_context(LINES, before=2, after=2, predicate=lambda l: False)
        assert result == []

    def test_overlapping_context_no_duplicates(self):
        """When before/after windows overlap, lines should appear once."""
        result = collect_context(LINES, before=2, after=2, predicate=is_error)
        lines_only = [ln for ln, _ in result]
        assert len(lines_only) == len(set(lines_only))

    def test_before_clipped_at_start(self):
        result = collect_context(LINES, before=10, predicate=is_error)
        lines_only = [ln for ln, _ in result]
        assert "alpha" in lines_only

    def test_after_clipped_at_end(self):
        result = collect_context(LINES, after=10, predicate=is_error)
        lines_only = [ln for ln, _ in result]
        assert "delta" in lines_only

    def test_negative_before_treated_as_zero(self):
        result = collect_context(LINES, before=-5, predicate=is_error)
        lines_only = [ln for ln, _ in result]
        assert "alpha" not in lines_only
