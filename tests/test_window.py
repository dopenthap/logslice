"""Tests for logslice.window."""

import pytest
from logslice.window import tumbling_window, sliding_window, window_reduce


def collect(gen):
    return list(gen)


# ---------------------------------------------------------------------------
# tumbling_window
# ---------------------------------------------------------------------------

class TestTumblingWindow:
    def test_empty_input_yields_nothing(self):
        assert collect(tumbling_window([], 3)) == []

    def test_exact_multiple(self):
        lines = ["a", "b", "c", "d"]
        result = collect(tumbling_window(lines, 2))
        assert result == [["a", "b"], ["c", "d"]]

    def test_remainder_forms_last_chunk(self):
        lines = ["a", "b", "c", "d", "e"]
        result = collect(tumbling_window(lines, 2))
        assert result == [["a", "b"], ["c", "d"], ["e"]]

    def test_size_one_yields_single_element_windows(self):
        lines = ["x", "y", "z"]
        result = collect(tumbling_window(lines, 1))
        assert result == [["x"], ["y"], ["z"]]

    def test_size_larger_than_input_yields_one_window(self):
        lines = ["a", "b"]
        result = collect(tumbling_window(lines, 10))
        assert result == [["a", "b"]]

    def test_zero_size_raises(self):
        with pytest.raises(ValueError):
            collect(tumbling_window(["a"], 0))


# ---------------------------------------------------------------------------
# sliding_window
# ---------------------------------------------------------------------------

class TestSlidingWindow:
    def test_empty_input_yields_nothing(self):
        assert collect(sliding_window([], 3)) == []

    def test_step_one_default(self):
        lines = ["a", "b", "c", "d"]
        result = collect(sliding_window(lines, 2))
        assert result == [["a", "b"], ["b", "c"], ["c", "d"]]

    def test_step_equals_size_behaves_like_tumbling(self):
        lines = ["a", "b", "c", "d"]
        result = collect(sliding_window(lines, 2, step=2))
        assert result == [["a", "b"], ["c", "d"]]

    def test_fewer_lines_than_size_yields_partial(self):
        result = collect(sliding_window(["a", "b"], 5))
        assert result == [["a", "b"]]

    def test_zero_size_raises(self):
        with pytest.raises(ValueError):
            collect(sliding_window(["a"], 0))

    def test_zero_step_raises(self):
        with pytest.raises(ValueError):
            collect(sliding_window(["a"], 2, step=0))

    def test_step_larger_than_size(self):
        lines = ["a", "b", "c", "d", "e", "f"]
        result = collect(sliding_window(lines, 2, step=3))
        assert result == [["a", "b"], ["d", "e"]]


# ---------------------------------------------------------------------------
# window_reduce
# ---------------------------------------------------------------------------

class TestWindowReduce:
    def test_join_reducer(self):
        windows = [["a", "b"], ["c", "d"]]
        result = collect(window_reduce(windows, lambda w: "|".join(w)))
        assert result == ["a|b", "c|d"]

    def test_count_reducer(self):
        windows = [["x", "y", "z"], ["p"]]
        result = collect(window_reduce(windows, lambda w: str(len(w))))
        assert result == ["3", "1"]

    def test_empty_windows_yields_nothing(self):
        assert collect(window_reduce([], lambda w: "")) == []
