"""Tests for logslice.window_stats."""

from logslice.window_stats import (
    WindowSummary,
    summarize_windows,
    windows_above_threshold,
)


def collect(gen):
    return list(gen)


def is_error(line: str) -> bool:
    return "ERROR" in line


class TestWindowSummary:
    def test_match_rate_full(self):
        ws = WindowSummary(index=0, size=4, matched=4, lines=[])
        assert ws.match_rate == 1.0

    def test_match_rate_half(self):
        ws = WindowSummary(index=0, size=4, matched=2, lines=[])
        assert ws.match_rate == 0.5

    def test_match_rate_zero_size(self):
        ws = WindowSummary(index=0, size=0, matched=0, lines=[])
        assert ws.match_rate == 0.0


class TestSummarizeWindows:
    def _lines(self):
        return [
            "INFO start",
            "ERROR bad thing",
            "INFO ok",
            "ERROR another",
            "INFO done",
            "ERROR last",
        ]

    def test_tumbling_window_count(self):
        summaries = collect(summarize_windows(self._lines(), 2, is_error))
        assert len(summaries) == 3

    def test_tumbling_matched_counts(self):
        summaries = collect(summarize_windows(self._lines(), 2, is_error))
        assert summaries[0].matched == 1  # INFO, ERROR
        assert summaries[1].matched == 1  # INFO, ERROR
        assert summaries[2].matched == 1  # INFO, ERROR

    def test_tumbling_index_increments(self):
        summaries = collect(summarize_windows(self._lines(), 2, is_error))
        assert [s.index for s in summaries] == [0, 1, 2]

    def test_sliding_window_count(self):
        summaries = collect(
            summarize_windows(self._lines(), 3, is_error, sliding=True, step=1)
        )
        # 6 lines, size=3, step=1 -> windows at positions 0,1,2,3
        assert len(summaries) == 4

    def test_lines_stored_in_summary(self):
        lines = ["a", "b", "c"]
        summaries = collect(summarize_windows(lines, 3, lambda l: l == "b"))
        assert summaries[0].lines == ["a", "b", "c"]

    def test_empty_input_yields_nothing(self):
        assert collect(summarize_windows([], 3, is_error)) == []


class TestWindowsAboveThreshold:
    def _make_summary(self, idx, size, matched):
        return WindowSummary(index=idx, size=size, matched=matched, lines=[])

    def test_all_above(self):
        summaries = [
            self._make_summary(0, 4, 4),
            self._make_summary(1, 4, 3),
        ]
        result = collect(windows_above_threshold(summaries, 0.5))
        assert len(result) == 2

    def test_none_above(self):
        summaries = [
            self._make_summary(0, 4, 0),
            self._make_summary(1, 4, 1),
        ]
        result = collect(windows_above_threshold(summaries, 0.9))
        assert result == []

    def test_exact_threshold_included(self):
        summaries = [self._make_summary(0, 4, 2)]  # rate == 0.5
        result = collect(windows_above_threshold(summaries, 0.5))
        assert len(result) == 1
