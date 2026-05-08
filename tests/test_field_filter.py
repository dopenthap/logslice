"""Tests for logslice.field_filter."""

import pytest
from logslice.field_filter import (
    field_equals,
    field_matches,
    kv_equals,
    kv_matches,
    make_field_predicate,
)


LOG_LINES = [
    "INFO  server started port=8080\n",
    "ERROR database connection failed port=5432\n",
    "INFO  request received method=GET status=200\n",
    "WARN  slow query method=POST status=503\n",
]


# ---------------------------------------------------------------------------
# field_equals
# ---------------------------------------------------------------------------

class TestFieldEquals:
    def test_matches_first_field(self):
        result = list(field_equals(LOG_LINES, 0, "INFO"))
        assert len(result) == 2
        assert all(r.startswith("INFO") for r in result)

    def test_no_match_returns_empty(self):
        result = list(field_equals(LOG_LINES, 0, "DEBUG"))
        assert result == []

    def test_empty_input(self):
        assert list(field_equals([], 0, "INFO")) == []

    def test_custom_separator(self):
        lines = ["a,b,c\n", "x,b,z\n", "a,q,c\n"]
        result = list(field_equals(lines, 1, "b", sep=","))
        assert len(result) == 2


# ---------------------------------------------------------------------------
# field_matches
# ---------------------------------------------------------------------------

class TestFieldMatches:
    def test_regex_on_second_field(self):
        result = list(field_matches(LOG_LINES, 1, r"^(server|database)"))
        assert len(result) == 2

    def test_out_of_range_field_excluded(self):
        result = list(field_matches(LOG_LINES, 99, r".*"))
        assert result == []

    def test_empty_input(self):
        assert list(field_matches([], 0, r".*")) == []


# ---------------------------------------------------------------------------
# kv_equals
# ---------------------------------------------------------------------------

class TestKvEquals:
    def test_match_by_key_value(self):
        result = list(kv_equals(LOG_LINES, "status", "200"))
        assert len(result) == 1
        assert "method=GET" in result[0]

    def test_no_match(self):
        result = list(kv_equals(LOG_LINES, "status", "404"))
        assert result == []

    def test_key_not_present(self):
        result = list(kv_equals(LOG_LINES, "nonexistent", "val"))
        assert result == []

    def test_empty_input(self):
        assert list(kv_equals([], "k", "v")) == []


# ---------------------------------------------------------------------------
# kv_matches
# ---------------------------------------------------------------------------

class TestKvMatches:
    def test_regex_on_kv(self):
        result = list(kv_matches(LOG_LINES, "status", r"^5"))
        assert len(result) == 1
        assert "503" in result[0]

    def test_no_match(self):
        result = list(kv_matches(LOG_LINES, "status", r"^9"))
        assert result == []


# ---------------------------------------------------------------------------
# make_field_predicate
# ---------------------------------------------------------------------------

class TestMakeFieldPredicate:
    def test_returns_true_on_match(self):
        pred = make_field_predicate(0, r"^(INFO|WARN)$")
        assert pred("INFO  something\n") is True

    def test_returns_false_on_no_match(self):
        pred = make_field_predicate(0, r"^DEBUG$")
        assert pred("INFO  something\n") is False

    def test_out_of_range_returns_false(self):
        pred = make_field_predicate(99, r".*")
        assert pred("short line\n") is False
