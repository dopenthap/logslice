"""Integration tests: window helpers wired into a pipeline-style flow."""

from logslice.window import tumbling_window, sliding_window, window_reduce
from logslice.window_stats import summarize_windows, windows_above_threshold


def _log_lines():
    return [
        "2024-01-01 INFO  service started",
        "2024-01-01 ERROR disk full",
        "2024-01-01 INFO  retrying",
        "2024-01-01 ERROR disk full again",
        "2024-01-01 ERROR third error",
        "2024-01-01 INFO  recovered",
        "2024-01-01 INFO  all good",
        "2024-01-01 ERROR one more",
    ]


def _is_error(line: str) -> bool:
    return "ERROR" in line


def collect(gen):
    return list(gen)


class TestWindowPipeline:
    def test_tumbling_then_reduce_to_counts(self):
        windows = tumbling_window(_log_lines(), 4)
        counts = collect(window_reduce(windows, lambda w: str(sum(1 for l in w if _is_error(l)))))
        assert counts == ["2", "2"]

    def test_sliding_error_density(self):
        summaries = collect(
            summarize_windows(_log_lines(), 3, _is_error, sliding=True, step=2)
        )
        # windows start at lines 0,2,4,6
        assert len(summaries) == 4
        rates = [s.match_rate for s in summaries]
        assert all(0.0 <= r <= 1.0 for r in rates)

    def test_filter_hot_windows(self):
        """Windows with >= 50% errors should be flagged."""
        summaries = summarize_windows(_log_lines(), 2, _is_error)
        hot = collect(windows_above_threshold(summaries, 0.5))
        # windows: (INFO,ERROR)->0.5, (INFO,ERROR)->0.5, (ERROR,INFO)->0.5, (INFO,ERROR)->0.5
        assert len(hot) == 4

    def test_pipeline_produces_no_output_for_empty_stream(self):
        summaries = collect(summarize_windows([], 3, _is_error))
        hot = collect(windows_above_threshold(summaries, 0.1))
        assert hot == []

    def test_window_lines_recoverable_from_summary(self):
        summaries = collect(summarize_windows(_log_lines(), 4, _is_error))
        all_lines = [ln for s in summaries for ln in s.lines]
        assert all_lines == _log_lines()
