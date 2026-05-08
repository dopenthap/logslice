"""Tests for logslice.truncator."""

from __future__ import annotations

import pytest

from logslice.truncator import (
    DEFAULT_MAX_LENGTH,
    truncate_line,
    truncate_lines,
    truncate_lines_conditional,
)


# ---------------------------------------------------------------------------
# truncate_line
# ---------------------------------------------------------------------------

class TestTruncateLine:
    def test_short_line_unchanged(self):
        line = "hello world"
        assert truncate_line(line, max_length=50) == line

    def test_exact_length_unchanged(self):
        line = "a" * 10
        assert truncate_line(line, max_length=10) == line

    def test_long_line_is_cut(self):
        line = "a" * 20
        result = truncate_line(line, max_length=10)
        assert result == "a" * 10 + "..."

    def test_trailing_newline_preserved_when_short(self):
        line = "hello\n"
        result = truncate_line(line, max_length=50)
        assert result.endswith("\n")
        assert result == "hello\n"

    def test_trailing_newline_preserved_after_truncation(self):
        line = "x" * 30 + "\n"
        result = truncate_line(line, max_length=10)
        assert result.endswith("\n")
        assert result == "x" * 10 + "...\n"

    def test_no_trailing_newline_not_added(self):
        line = "y" * 30
        result = truncate_line(line, max_length=10)
        assert not result.endswith("\n")

    def test_ellipsis_suffix(self):
        line = "abcdefghij"
        result = truncate_line(line, max_length=5)
        assert result.endswith("...")

    def test_default_max_length(self):
        short = "z" * DEFAULT_MAX_LENGTH
        assert truncate_line(short) == short
        long_line = "z" * (DEFAULT_MAX_LENGTH + 1)
        assert len(truncate_line(long_line)) == DEFAULT_MAX_LENGTH + len("...")

    def test_invalid_max_length_raises(self):
        with pytest.raises(ValueError):
            truncate_line("hello", max_length=0)

    def test_negative_max_length_raises(self):
        with pytest.raises(ValueError):
            truncate_line("hello", max_length=-5)


# ---------------------------------------------------------------------------
# truncate_lines
# ---------------------------------------------------------------------------

class TestTruncateLines:
    def test_empty_input_yields_nothing(self):
        assert list(truncate_lines([], max_length=10)) == []

    def test_all_short_lines_unchanged(self):
        lines = ["foo\n", "bar\n", "baz\n"]
        assert list(truncate_lines(lines, max_length=50)) == lines

    def test_mixed_lines_truncated_correctly(self):
        lines = ["short\n", "a" * 20 + "\n"]
        result = list(truncate_lines(lines, max_length=10))
        assert result[0] == "short\n"
        assert result[1] == "a" * 10 + "...\n"

    def test_returns_iterator(self):
        import types
        result = truncate_lines(["hello"], max_length=10)
        assert isinstance(result, types.GeneratorType)


# ---------------------------------------------------------------------------
# truncate_lines_conditional
# ---------------------------------------------------------------------------

class TestTruncateLinesConditional:
    def test_none_max_length_passes_through_unchanged(self):
        lines = ["a" * 300 + "\n", "b" * 300]
        result = list(truncate_lines_conditional(lines, max_length=None))
        assert result == lines

    def test_with_max_length_truncates(self):
        lines = ["a" * 20]
        result = list(truncate_lines_conditional(lines, max_length=10))
        assert result == ["a" * 10 + "..."]
