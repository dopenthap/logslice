"""Tests for logslice.output."""

import io
import json

from logslice.output import write_lines, write_output


def make_stream():
    return io.StringIO()


class TestWriteLines:
    def test_plain_output(self):
        buf = make_stream()
        count = write_lines(["line one\n", "line two\n"], out=buf)
        assert count == 2
        assert buf.getvalue() == "line one\nline two\n"

    def test_json_output(self):
        buf = make_stream()
        write_lines(["hello"], fmt="json", out=buf)
        record = json.loads(buf.getvalue().strip())
        assert record["line"] == "hello"

    def test_csv_writes_header(self):
        buf = make_stream()
        write_lines(["data"], fmt="csv", out=buf)
        lines = buf.getvalue().splitlines()
        assert lines[0] == 'n,"line"'

    def test_line_numbers(self):
        buf = make_stream()
        write_lines(["a", "b"], show_line_numbers=True, out=buf)
        lines = buf.getvalue().splitlines()
        assert lines[0] == "1: a"
        assert lines[1] == "2: b"

    def test_empty_input_returns_zero(self):
        buf = make_stream()
        count = write_lines([], out=buf)
        assert count == 0
        assert buf.getvalue() == ""


class TestWriteOutput:
    def test_returns_matched_count(self):
        buf = make_stream()
        count = write_output(["x", "y", "z"], out=buf, total=10)
        assert count == 3

    def test_summary_appended(self):
        buf = make_stream()
        write_output(["a", "b"], out=buf, total=50, show_summary=True)
        assert "matched 2/50" in buf.getvalue()

    def test_no_summary_when_disabled(self):
        buf = make_stream()
        write_output(["a"], out=buf, total=10, show_summary=False)
        assert "matched" not in buf.getvalue()
