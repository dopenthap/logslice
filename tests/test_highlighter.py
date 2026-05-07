"""Tests for logslice.highlighter."""

import pytest

from logslice.highlighter import (
    ANSI_BOLD_GREEN,
    ANSI_BOLD_RED,
    ANSI_BOLD_YELLOW,
    ANSI_RESET,
    highlight_lines,
    highlight_match,
    strip_ansi,
)


class TestHighlightMatch:
    def test_wraps_match_with_default_red(self):
        result = highlight_match("ERROR occurred", "ERROR")
        assert result == f"{ANSI_BOLD_RED}ERROR{ANSI_RESET} occurred"

    def test_wraps_match_yellow(self):
        result = highlight_match("WARN something", "WARN", color="yellow")
        assert result == f"{ANSI_BOLD_YELLOW}WARN{ANSI_RESET} something"

    def test_wraps_match_green(self):
        result = highlight_match("OK done", "OK", color="green")
        assert result == f"{ANSI_BOLD_GREEN}OK{ANSI_RESET} done"

    def test_unknown_color_falls_back_to_red(self):
        result = highlight_match("ERROR", "ERROR", color="purple")
        assert result.startswith(ANSI_BOLD_RED)

    def test_multiple_occurrences_all_highlighted(self):
        result = highlight_match("a a a", "a")
        assert result.count(ANSI_BOLD_RED) == 3
        assert result.count(ANSI_RESET) == 3

    def test_empty_pattern_returns_line_unchanged(self):
        line = "no pattern here"
        assert highlight_match(line, "") == line

    def test_invalid_regex_returns_line_unchanged(self):
        line = "some log line"
        assert highlight_match(line, "[") == line

    def test_no_match_returns_line_unchanged(self):
        result = highlight_match("nothing here", "ERROR")
        assert result == "nothing here"

    def test_regex_group_highlight(self):
        result = highlight_match("code=404 msg=not found", r"\d+")
        assert f"{ANSI_BOLD_RED}404{ANSI_RESET}" in result


class TestStripAnsi:
    def test_removes_color_codes(self):
        colored = f"{ANSI_BOLD_RED}ERROR{ANSI_RESET} happened"
        assert strip_ansi(colored) == "ERROR happened"

    def test_plain_text_unchanged(self):
        assert strip_ansi("plain text") == "plain text"

    def test_multiple_codes_stripped(self):
        text = f"{ANSI_BOLD_RED}A{ANSI_RESET}{ANSI_BOLD_YELLOW}B{ANSI_RESET}"
        assert strip_ansi(text) == "AB"


class TestHighlightLines:
    def test_none_pattern_returns_original_list(self):
        lines = ["line one", "line two"]
        assert highlight_lines(lines, None) == lines

    def test_empty_pattern_returns_original_list(self):
        lines = ["line one"]
        assert highlight_lines(lines, "") == lines

    def test_highlights_each_line(self):
        lines = ["ERROR here", "all good", "ERROR again"]
        result = highlight_lines(lines, "ERROR")
        assert ANSI_BOLD_RED in result[0]
        assert ANSI_BOLD_RED not in result[1]
        assert ANSI_BOLD_RED in result[2]

    def test_returns_new_list(self):
        lines = ["ERROR"]
        result = highlight_lines(lines, "ERROR")
        assert result is not lines
