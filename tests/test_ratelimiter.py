"""Tests for logslice.ratelimiter."""

import pytest
from logslice.ratelimiter import rate_limit_lines, burst_limit_lines


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_clock(values):
    it = iter(values)
    def clock():
        return next(it)
    return clock


def collect(gen):
    return list(gen)


# ---------------------------------------------------------------------------
# rate_limit_lines
# ---------------------------------------------------------------------------

class TestRateLimitLines:
    def test_zero_rate_yields_all_immediately(self):
        lines = ["a", "b", "c"]
        slept = []
        result = collect(rate_limit_lines(lines, 0, _sleep=slept.append))
        assert result == lines
        assert slept == []

    def test_negative_rate_yields_all_immediately(self):
        lines = ["x", "y"]
        result = collect(rate_limit_lines(lines, -5))
        assert result == lines

    def test_all_lines_yielded_at_positive_rate(self):
        lines = ["a", "b", "c", "d"]
        slept = []
        # clock always returns 0 so wait will always be positive after first
        clock_values = [0.0] * 20
        result = collect(
            rate_limit_lines(
                lines,
                2.0,
                _clock=_make_clock(clock_values),
                _sleep=slept.append,
            )
        )
        assert result == lines

    def test_no_sleep_when_lines_arrive_slowly(self):
        """If clock advances faster than the rate, no sleeping should occur."""
        lines = ["a", "b", "c"]
        # Each successive call returns a time well past the next_allowed
        clock_values = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        slept = []
        collect(
            rate_limit_lines(
                lines,
                1.0,
                _clock=_make_clock(clock_values),
                _sleep=slept.append,
            )
        )
        assert slept == []

    def test_sleep_called_when_lines_arrive_too_fast(self):
        lines = ["a", "b", "c"]
        # clock never advances — every line arrives at t=0
        clock_values = [0.0] * 20
        slept = []
        collect(
            rate_limit_lines(
                lines,
                1.0,
                _clock=_make_clock(clock_values),
                _sleep=slept.append,
            )
        )
        assert len(slept) > 0


# ---------------------------------------------------------------------------
# burst_limit_lines
# ---------------------------------------------------------------------------

class TestBurstLimitLines:
    def test_zero_burst_yields_all(self):
        lines = ["a", "b", "c"]
        result = collect(burst_limit_lines(lines, 0, 1.0))
        assert result == lines

    def test_zero_window_yields_all(self):
        lines = ["a", "b", "c"]
        result = collect(burst_limit_lines(lines, 10, 0))
        assert result == lines

    def test_burst_within_window_no_sleep(self):
        lines = ["a", "b", "c"]
        slept = []
        # clock advances steadily; 3 lines fit in burst of 5
        clock_values = [0.0, 0.1, 0.2, 0.3, 0.4]
        collect(
            burst_limit_lines(
                lines,
                5,
                1.0,
                _clock=_make_clock(clock_values),
                _sleep=slept.append,
            )
        )
        assert slept == []

    def test_burst_exceeded_causes_sleep(self):
        lines = list("abcde")
        slept = []
        # clock stays at 0 so window never expires naturally
        clock_values = [0.0] * 30
        collect(
            burst_limit_lines(
                lines,
                2,
                1.0,
                _clock=_make_clock(clock_values),
                _sleep=slept.append,
            )
        )
        assert len(slept) > 0

    def test_all_lines_yielded_despite_throttling(self):
        lines = list("abcdef")
        clock_values = [0.0] * 40
        result = collect(
            burst_limit_lines(
                lines,
                2,
                1.0,
                _clock=_make_clock(clock_values),
                _sleep=lambda _: None,
            )
        )
        assert result == lines
