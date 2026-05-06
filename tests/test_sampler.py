"""Tests for logslice.sampler."""

import pytest

from logslice.sampler import sample_every_nth, sample_lines


LINES = [f"line {i}\n" for i in range(100)]


# ---------------------------------------------------------------------------
# sample_lines
# ---------------------------------------------------------------------------


class TestSampleLines:
    def test_rate_zero_yields_nothing(self):
        result = list(sample_lines(LINES, rate=0.0))
        assert result == []

    def test_rate_one_yields_all(self):
        result = list(sample_lines(LINES, rate=1.0))
        assert result == LINES

    def test_approximate_rate(self):
        result = list(sample_lines(LINES, rate=0.5, seed=42))
        # With seed=42 and 100 lines at 50% we expect roughly 40–60 lines.
        assert 30 <= len(result) <= 70

    def test_seed_reproducibility(self):
        a = list(sample_lines(LINES, rate=0.3, seed=7))
        b = list(sample_lines(LINES, rate=0.3, seed=7))
        assert a == b

    def test_different_seeds_differ(self):
        a = list(sample_lines(LINES, rate=0.5, seed=1))
        b = list(sample_lines(LINES, rate=0.5, seed=2))
        # Very unlikely to be identical across 100 lines.
        assert a != b

    def test_invalid_rate_low(self):
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            list(sample_lines(LINES, rate=-0.1))

    def test_invalid_rate_high(self):
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            list(sample_lines(LINES, rate=1.1))

    def test_empty_input(self):
        assert list(sample_lines([], rate=0.5)) == []


# ---------------------------------------------------------------------------
# sample_every_nth
# ---------------------------------------------------------------------------


class TestSampleEveryNth:
    def test_n_equals_one_yields_all(self):
        result = list(sample_every_nth(LINES, n=1))
        assert result == LINES

    def test_n_equals_two(self):
        result = list(sample_every_nth(LINES, n=2))
        assert result == LINES[::2]

    def test_n_equals_ten(self):
        result = list(sample_every_nth(LINES, n=10))
        assert len(result) == 10
        assert result[0] == LINES[0]
        assert result[1] == LINES[10]

    def test_n_larger_than_input(self):
        small = ["a", "b", "c"]
        result = list(sample_every_nth(small, n=10))
        assert result == ["a"]

    def test_invalid_n_zero(self):
        with pytest.raises(ValueError, match=">= 1"):
            list(sample_every_nth(LINES, n=0))

    def test_invalid_n_negative(self):
        with pytest.raises(ValueError, match=">= 1"):
            list(sample_every_nth(LINES, n=-5))

    def test_empty_input(self):
        assert list(sample_every_nth([], n=3)) == []
