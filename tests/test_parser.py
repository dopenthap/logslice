"""Tests for logslice.parser module."""

from datetime import datetime

import pytest

from logslice.parser import extract_timestamp, matches_pattern, parse_line


class TestExtractTimestamp:
    def test_iso_format(self):
        line = "2024-03-15T12:34:56 INFO server started"
        ts = extract_timestamp(line)
        assert ts == datetime(2024, 3, 15, 12, 34, 56)

    def test_space_separated_format(self):
        line = "2024-03-15 08:00:00 ERROR disk full"
        ts = extract_timestamp(line)
        assert ts == datetime(2024, 3, 15, 8, 0, 0)

    def test_no_timestamp_returns_none(self):
        line = "no timestamp here at all"
        assert extract_timestamp(line) is None

    def test_nginx_format(self):
        line = '192.168.1.1 - - [15/Mar/2024:10:20:30 +0000] "GET / HTTP/1.1" 200'
        ts = extract_timestamp(line)
        assert ts == datetime(2024, 3, 15, 10, 20, 30)


class TestMatchesPattern:
    def test_simple_match(self):
        assert matches_pattern("ERROR: disk full", r"ERROR") is True

    def test_no_match(self):
        assert matches_pattern("INFO: all good", r"ERROR") is False

    def test_case_sensitive_default(self):
        assert matches_pattern("error occurred", r"ERROR") is False

    def test_ignore_case(self):
        assert matches_pattern("error occurred", r"ERROR", ignore_case=True) is True

    def test_invalid_pattern_raises(self):
        with pytest.raises(ValueError, match="Invalid regex"):
            matches_pattern("some line", r"[invalid")


class TestParseLine:
    def test_returns_dict_with_keys(self):
        result = parse_line("2024-01-01T00:00:00 hello\n")
        assert "raw" in result
        assert "timestamp" in result

    def test_strips_newline(self):
        result = parse_line("hello\n")
        assert result["raw"] == "hello"
