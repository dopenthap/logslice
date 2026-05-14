"""Tests for logslice.tagger."""

from __future__ import annotations

import pytest

from logslice.tagger import (
    compile_rules,
    filter_by_tag,
    tag_all,
    tag_line,
    tag_lines,
)


RULES = compile_rules(
    {
        "error": r"ERROR",
        "warn": r"WARN",
        "info": r"INFO",
    }
)


def collect(it):
    return list(it)


# ---------------------------------------------------------------------------
# tag_line
# ---------------------------------------------------------------------------

class TestTagLine:
    def test_matches_error(self):
        assert tag_line("2024-01-01 ERROR something broke", RULES) == "error"

    def test_matches_warn(self):
        assert tag_line("2024-01-01 WARN low memory", RULES) == "warn"

    def test_no_match_returns_none(self):
        assert tag_line("2024-01-01 DEBUG verbose", RULES) is None

    def test_first_rule_wins(self):
        # line contains both ERROR and WARN; error rule is first
        assert tag_line("ERROR WARN both present", RULES) == "error"


# ---------------------------------------------------------------------------
# tag_all
# ---------------------------------------------------------------------------

class TestTagAll:
    def test_single_match(self):
        assert tag_all("ERROR only", RULES) == ["error"]

    def test_multiple_matches(self):
        result = tag_all("ERROR WARN together", RULES)
        assert "error" in result
        assert "warn" in result

    def test_no_match_returns_empty(self):
        assert tag_all("nothing here", RULES) == []


# ---------------------------------------------------------------------------
# tag_lines
# ---------------------------------------------------------------------------

class TestTagLines:
    def test_prepends_tag_single(self):
        lines = ["ERROR bad thing\n"]
        result = collect(tag_lines(lines, RULES))
        assert result == ["[error] ERROR bad thing\n"]

    def test_untagged_line_unchanged(self):
        lines = ["DEBUG verbose output\n"]
        result = collect(tag_lines(lines, RULES))
        assert result == ["DEBUG verbose output\n"]

    def test_multi_tag_joined(self):
        lines = ["ERROR WARN both\n"]
        result = collect(tag_lines(lines, RULES, multi=True))
        assert "error" in result[0]
        assert "warn" in result[0]

    def test_custom_prefix(self):
        lines = ["INFO startup\n"]
        result = collect(tag_lines(lines, RULES, prefix="<{tag}> "))
        assert result[0].startswith("<info> ")

    def test_trailing_newline_preserved(self):
        lines = ["WARN disk full\n"]
        result = collect(tag_lines(lines, RULES))
        assert result[0].endswith("\n")

    def test_no_newline_preserved(self):
        lines = ["WARN disk full"]
        result = collect(tag_lines(lines, RULES))
        assert not result[0].endswith("\n")

    def test_empty_input_yields_nothing(self):
        assert collect(tag_lines([], RULES)) == []


# ---------------------------------------------------------------------------
# filter_by_tag
# ---------------------------------------------------------------------------

class TestFilterByTag:
    def test_keeps_matching_tag(self):
        lines = ["ERROR bad\n", "INFO ok\n", "ERROR again\n"]
        result = collect(filter_by_tag(lines, RULES, "error"))
        assert len(result) == 2
        assert all("ERROR" in l for l in result)

    def test_excludes_other_tags(self):
        lines = ["WARN low\n", "ERROR bad\n"]
        result = collect(filter_by_tag(lines, RULES, "warn"))
        assert result == ["WARN low\n"]

    def test_no_matches_returns_empty(self):
        lines = ["DEBUG verbose\n"]
        result = collect(filter_by_tag(lines, RULES, "error"))
        assert result == []
