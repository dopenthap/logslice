"""Tests for logslice.merger."""

import pytest
from logslice.merger import merge_streams, merge_sorted_buffers


def collect(it):
    return list(it)


STREAM_A = [
    "2024-01-01T00:00:01 INFO  alpha first\n",
    "2024-01-01T00:00:03 INFO  alpha third\n",
    "2024-01-01T00:00:05 INFO  alpha fifth\n",
]

STREAM_B = [
    "2024-01-01T00:00:02 INFO  beta second\n",
    "2024-01-01T00:00:04 INFO  beta fourth\n",
    "2024-01-01T00:00:06 INFO  beta sixth\n",
]


class TestMergeStreams:
    def test_empty_inputs_yield_nothing(self):
        assert collect(merge_streams([], [])) == []

    def test_single_stream_passthrough(self):
        assert collect(merge_streams(STREAM_A)) == STREAM_A

    def test_two_interleaved_streams_sorted_by_timestamp(self):
        result = collect(merge_streams(STREAM_A, STREAM_B))
        assert len(result) == 6
        assert "alpha first" in result[0]
        assert "beta second" in result[1]
        assert "alpha third" in result[2]
        assert "beta fourth" in result[3]
        assert "alpha fifth" in result[4]
        assert "beta sixth" in result[5]

    def test_lines_without_timestamps_sort_last(self):
        no_ts = ["no timestamp here\n", "also no timestamp\n"]
        result = collect(merge_streams(STREAM_A[:1], no_ts))
        assert "alpha first" in result[0]
        assert result[1:] == no_ts

    def test_stream_id_breaks_timestamp_ties(self):
        same_ts = [
            "2024-01-01T00:00:01 first stream\n",
        ]
        same_ts2 = [
            "2024-01-01T00:00:01 second stream\n",
        ]
        result = collect(merge_streams(same_ts, same_ts2))
        assert "first stream" in result[0]
        assert "second stream" in result[1]

    def test_three_streams(self):
        c = ["2024-01-01T00:00:07 gamma\n"]
        result = collect(merge_streams(STREAM_A, STREAM_B, c))
        assert len(result) == 7
        assert "gamma" in result[-1]


class TestMergeSortedBuffers:
    def test_no_duplicates_flag_keeps_all(self):
        buf = [["line one\n", "line two\n"], ["line three\n"]]
        result = collect(merge_sorted_buffers(buf, drop_duplicates=False))
        assert len(result) == 3

    def test_drop_duplicates_removes_exact_repeats(self):
        dup_line = "2024-01-01T00:00:01 INFO dup\n"
        buf = [[dup_line], [dup_line]]
        result = collect(merge_sorted_buffers(buf, drop_duplicates=True))
        assert result == [dup_line]

    def test_drop_duplicates_keeps_distinct_lines(self):
        buf = [
            ["2024-01-01T00:00:01 INFO a\n"],
            ["2024-01-01T00:00:02 INFO b\n"],
        ]
        result = collect(merge_sorted_buffers(buf, drop_duplicates=True))
        assert len(result) == 2

    def test_empty_buffers(self):
        assert collect(merge_sorted_buffers([])) == []
