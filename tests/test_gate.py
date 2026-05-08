"""Tests for logslice.gate."""

import pytest
from logslice.gate import gate_lines, toggle_gate, limit_lines, skip_lines


def collect(gen):
    return list(gen)


# ---------------------------------------------------------------------------
# gate_lines
# ---------------------------------------------------------------------------

class TestGateLines:
    def test_always_true_passes_all(self):
        lines = ["a", "b", "c"]
        assert collect(gate_lines(iter(lines), lambda _: True)) == lines

    def test_always_false_passes_none(self):
        lines = ["a", "b", "c"]
        assert collect(gate_lines(iter(lines), lambda _: False)) == []

    def test_stateful_predicate(self):
        """Predicate that opens after seeing 'START'."""
        state = {"open": False}
        def pred(line):
            if "START" in line:
                state["open"] = True
            return state["open"]
        lines = ["before", "START", "after"]
        assert collect(gate_lines(iter(lines), pred)) == ["START", "after"]

    def test_empty_input(self):
        assert collect(gate_lines(iter([]), lambda _: True)) == []


# ---------------------------------------------------------------------------
# toggle_gate
# ---------------------------------------------------------------------------

class TestToggleGate:
    def test_no_patterns_yields_all(self):
        lines = ["a", "b", "c"]
        assert collect(toggle_gate(iter(lines))) == lines

    def test_start_pattern_delays_output(self):
        lines = ["before", "BEGIN", "inside", "after"]
        result = collect(toggle_gate(iter(lines), start_pattern="BEGIN"))
        assert result == ["BEGIN", "inside", "after"]

    def test_stop_pattern_ends_output(self):
        lines = ["a", "END", "b"]
        result = collect(toggle_gate(iter(lines), stop_pattern="END"))
        assert result == ["a", "END"]

    def test_start_and_stop_pattern(self):
        lines = ["skip", "START here", "keep", "STOP here", "skip too"]
        result = collect(
            toggle_gate(iter(lines), start_pattern="START", stop_pattern="STOP")
        )
        assert result == ["START here", "keep", "STOP here"]

    def test_no_start_match_yields_nothing(self):
        lines = ["a", "b", "c"]
        result = collect(toggle_gate(iter(lines), start_pattern="NEVER"))
        assert result == []

    def test_multiple_sections(self):
        lines = ["BEGIN", "x", "END", "gap", "BEGIN", "y", "END"]
        result = collect(
            toggle_gate(iter(lines), start_pattern="BEGIN", stop_pattern="END")
        )
        assert result == ["BEGIN", "x", "END", "BEGIN", "y", "END"]


# ---------------------------------------------------------------------------
# limit_lines
# ---------------------------------------------------------------------------

class TestLimitLines:
    def test_zero_limit_yields_nothing(self):
        assert collect(limit_lines(iter(["a", "b"]), 0)) == []

    def test_negative_limit_yields_nothing(self):
        assert collect(limit_lines(iter(["a", "b"]), -1)) == []

    def test_limit_less_than_total(self):
        assert collect(limit_lines(iter(["a", "b", "c", "d"]), 2)) == ["a", "b"]

    def test_limit_greater_than_total(self):
        assert collect(limit_lines(iter(["a", "b"]), 10)) == ["a", "b"]

    def test_exact_limit(self):
        assert collect(limit_lines(iter(["a", "b", "c"]), 3)) == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# skip_lines
# ---------------------------------------------------------------------------

class TestSkipLines:
    def test_skip_zero_yields_all(self):
        lines = ["a", "b", "c"]
        assert collect(skip_lines(iter(lines), 0)) == lines

    def test_skip_some(self):
        assert collect(skip_lines(iter(["a", "b", "c", "d"]), 2)) == ["c", "d"]

    def test_skip_more_than_available(self):
        assert collect(skip_lines(iter(["a", "b"]), 10)) == []

    def test_skip_exact(self):
        assert collect(skip_lines(iter(["a", "b", "c"]), 3)) == []
