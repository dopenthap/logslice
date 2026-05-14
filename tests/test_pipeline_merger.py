"""Integration tests: merger wired into the broader pipeline helpers."""

from logslice.merger import merge_streams
from logslice.filter import filter_lines
from logslice.highlighter import highlight_lines


def collect(it):
    return list(it)


APP_LOG = [
    "2024-03-01T08:00:01 INFO  app started\n",
    "2024-03-01T08:00:05 ERROR app crashed\n",
    "2024-03-01T08:00:09 INFO  app recovered\n",
]

SYS_LOG = [
    "2024-03-01T08:00:03 WARN  disk usage high\n",
    "2024-03-01T08:00:07 ERROR oom killer invoked\n",
]


class TestMergerPipelineIntegration:
    def test_merge_then_filter_errors(self):
        merged = merge_streams(APP_LOG, SYS_LOG)
        errors = collect(filter_lines(merged, pattern=r"ERROR"))
        assert len(errors) == 2
        assert all("ERROR" in l for l in errors)

    def test_merge_preserves_chronological_order(self):
        result = collect(merge_streams(APP_LOG, SYS_LOG))
        timestamps = [l.split()[0] for l in result]
        assert timestamps == sorted(timestamps)

    def test_merge_then_highlight_marks_errors(self):
        merged = merge_streams(APP_LOG, SYS_LOG)
        highlighted = collect(highlight_lines(merged, pattern=r"ERROR", color="red"))
        error_lines = [l for l in highlighted if "ERROR" in l]
        assert all("\033[" in l for l in error_lines), "errors should be ANSI-highlighted"

    def test_empty_second_stream_acts_as_passthrough(self):
        result = collect(merge_streams(APP_LOG, []))
        assert result == APP_LOG

    def test_merge_all_no_timestamp_streams(self):
        a = ["foo\n", "bar\n"]
        b = ["baz\n"]
        result = collect(merge_streams(a, b))
        assert set(result) == {"foo\n", "bar\n", "baz\n"}
