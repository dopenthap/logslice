"""Tests for sampling integration inside filter_lines."""

import pytest

from logslice.filter import filter_lines


ERROR_LINES = [f"2024-01-01T00:00:{i:02d} ERROR msg {i}\n" for i in range(60)]
INFO_LINES = [f"2024-01-01T00:00:{i:02d} INFO msg {i}\n" for i in range(60)]
MIXED_LINES = ERROR_LINES + INFO_LINES


class TestFilterWithSampleRate:
    def test_sample_rate_one_keeps_all(self):
        result = list(filter_lines(ERROR_LINES, sample_rate=1.0))
        assert result == ERROR_LINES

    def test_sample_rate_zero_keeps_none(self):
        result = list(filter_lines(ERROR_LINES, sample_rate=0.0))
        assert result == []

    def test_sample_rate_with_pattern(self):
        # Only ERROR lines pass the pattern, then sampled at 50%.
        result = list(
            filter_lines(MIXED_LINES, pattern="ERROR", sample_rate=0.5, sample_seed=99)
        )
        # All returned lines must contain ERROR.
        assert all("ERROR" in ln for ln in result)
        # Expect roughly half of the 60 ERROR lines.
        assert 15 <= len(result) <= 55

    def test_sample_rate_reproducible(self):
        a = list(filter_lines(ERROR_LINES, sample_rate=0.4, sample_seed=3))
        b = list(filter_lines(ERROR_LINES, sample_rate=0.4, sample_seed=3))
        assert a == b

    def test_invalid_sample_rate_raises(self):
        with pytest.raises(ValueError):
            list(filter_lines(ERROR_LINES, sample_rate=2.0))


class TestFilterWithSampleNth:
    def test_every_first_keeps_all(self):
        result = list(filter_lines(ERROR_LINES, sample_nth=1))
        assert result == ERROR_LINES

    def test_every_second(self):
        result = list(filter_lines(ERROR_LINES, sample_nth=2))
        assert result == ERROR_LINES[::2]

    def test_every_nth_with_pattern(self):
        result = list(
            filter_lines(MIXED_LINES, pattern="INFO", sample_nth=3)
        )
        assert all("INFO" in ln for ln in result)
        assert len(result) == len(INFO_LINES[::3])

    def test_invalid_nth_raises(self):
        with pytest.raises(ValueError):
            list(filter_lines(ERROR_LINES, sample_nth=0))

    def test_nth_takes_priority_over_rate(self):
        # sample_nth should win when both are provided.
        result = list(filter_lines(ERROR_LINES, sample_nth=5, sample_rate=0.1))
        assert result == ERROR_LINES[::5]

    def test_empty_input(self):
        assert list(filter_lines([], sample_nth=2)) == []
        assert list(filter_lines([], sample_rate=0.5)) == []
