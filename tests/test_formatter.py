"""Tests for logslice.formatter."""

import json
import pytest

from logslice.formatter import (
    format_line,
    format_header,
    format_summary,
    SUPPORTED_FORMATS,
)


class TestFormatLinePlain:
    def test_plain_no_number(self):
        assert format_line("hello world") == "hello world"

    def test_plain_with_number(self):
        assert format_line("hello world", line_number=3) == "3: hello world"

    def test_strips_trailing_newline(self):
        assert format_line("hello\n") == "hello"


class TestFormatLineJson:
    def test_json_no_number(self):
        result = json.loads(format_line("msg", fmt="json"))
        assert result == {"line": "msg"}

    def test_json_with_number(self):
        result = json.loads(format_line("msg", fmt="json", line_number=7))
        assert result == {"line": "msg", "n": 7}


class TestFormatLineCsv:
    def test_csv_no_number(self):
        assert format_line("hello", fmt="csv") == '"hello"'

    def test_csv_with_number(self):
        assert format_line("hello", fmt="csv", line_number=2) == '2,"hello"'

    def test_csv_escapes_quotes(self):
        result = format_line('say "hi"', fmt="csv")
        assert result == '"say \"\"hi\"\""'


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        format_line("x", fmt="xml")


class TestFormatHeader:
    def test_csv_has_header(self):
        assert format_header("csv") == 'n,"line"'

    def test_plain_no_header(self):
        assert format_header("plain") is None

    def test_json_no_header(self):
        assert format_header("json") is None


class TestFormatSummary:
    def test_plain_summary(self):
        assert format_summary(5, 100) == "# matched 5/100 lines"

    def test_json_summary(self):
        result = json.loads(format_summary(5, 100, fmt="json"))
        assert result == {"matched": 5, "total": 100}

    def test_csv_summary(self):
        assert format_summary(5, 100, fmt="csv").startswith("#")
