"""Integration tests combining gate + ratelimiter with the pipeline."""

import io
import pytest

from logslice.gate import toggle_gate, limit_lines, skip_lines
from logslice.ratelimiter import rate_limit_lines


def _lines(*args):
    return list(args)


def collect(gen):
    return list(gen)


# ---------------------------------------------------------------------------
# gate + rate-limiter composition
# ---------------------------------------------------------------------------

class TestGateWithRateLimit:
    def test_gate_then_rate_limit(self):
        """Gate a section then rate-limit it — all lines should still arrive."""
        raw = ["skip", "START", "keep1", "keep2", "END", "skip2"]
        gated = toggle_gate(iter(raw), start_pattern="START", stop_pattern="END")
        throttled = rate_limit_lines(
            gated, 100.0, _sleep=lambda _: None
        )
        assert collect(throttled) == ["START", "keep1", "keep2", "END"]

    def test_limit_then_rate_limit(self):
        lines = [str(i) for i in range(20)]
        limited = limit_lines(iter(lines), 5)
        throttled = rate_limit_lines(limited, 0)  # 0 = no throttle
        assert collect(throttled) == [str(i) for i in range(5)]

    def test_skip_then_limit(self):
        lines = list("abcdefghij")
        skipped = skip_lines(iter(lines), 3)
        limited = limit_lines(skipped, 4)
        assert collect(limited) == ["d", "e", "f", "g"]


# ---------------------------------------------------------------------------
# edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_stream_through_gate(self):
        result = collect(toggle_gate(iter([]), start_pattern="X"))
        assert result == []

    def test_empty_stream_rate_limited(self):
        result = collect(rate_limit_lines(iter([]), 10.0))
        assert result == []

    def test_single_line_passes_gate(self):
        result = collect(toggle_gate(iter(["only"])))
        assert result == ["only"]

    def test_rate_limit_one_per_second_all_yielded(self):
        lines = ["x", "y", "z"]
        # clock returns increasing values so no actual sleep needed
        times = iter([0.0, 1.1, 2.2, 3.3, 4.4, 5.5])
        result = collect(
            rate_limit_lines(
                iter(lines),
                1.0,
                _clock=lambda: next(times),
                _sleep=lambda _: None,
            )
        )
        assert result == lines
