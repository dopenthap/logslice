"""Tests for logslice.router."""

import pytest
from logslice.router import make_router, route_lines, iter_routed


def is_error(line: str) -> bool:
    return "ERROR" in line


def is_warn(line: str) -> bool:
    return "WARN" in line


ROUTES = [("error", is_error), ("warn", is_warn)]
LINES = [
    "2024-01-01 ERROR something broke",
    "2024-01-01 WARN disk low",
    "2024-01-01 INFO all good",
    "2024-01-01 ERROR another failure",
]


class TestMakeRouter:
    def test_first_matching_route_wins(self):
        router = make_router(ROUTES)
        assert router("ERROR and WARN") == "error"

    def test_no_match_returns_none_by_default(self):
        router = make_router(ROUTES)
        assert router("INFO nothing here") is None

    def test_no_match_returns_default_key(self):
        router = make_router(ROUTES, default_key="other")
        assert router("INFO nothing here") == "other"

    def test_empty_routes_always_returns_default(self):
        router = make_router([], default_key="all")
        assert router("anything") == "all"

    def test_empty_routes_no_default_returns_none(self):
        router = make_router([])
        assert router("anything") is None


class TestRouteLines:
    def test_partitions_into_buckets(self):
        result = route_lines(LINES, ROUTES)
        assert len(result["error"]) == 2
        assert len(result["warn"]) == 1
        assert "other" not in result

    def test_unmatched_dropped_without_default(self):
        result = route_lines(LINES, ROUTES)
        assert "INFO all good" not in result.get("error", [])
        assert "INFO all good" not in result.get("warn", [])

    def test_unmatched_goes_to_default_key(self):
        result = route_lines(LINES, ROUTES, default_key="other")
        assert "2024-01-01 INFO all good" in result["other"]

    def test_empty_input_returns_empty_dict(self):
        assert route_lines([], ROUTES) == {}

    def test_all_match_same_bucket(self):
        lines = ["ERROR a", "ERROR b", "ERROR c"]
        result = route_lines(lines, ROUTES)
        assert result == {"error": lines}


class TestIterRouted:
    def test_yields_key_line_pairs(self):
        pairs = list(iter_routed(LINES, ROUTES))
        keys = [k for k, _ in pairs]
        assert keys == ["error", "warn", "error"]

    def test_skips_unmatched_without_default(self):
        pairs = list(iter_routed(["INFO ok"], ROUTES))
        assert pairs == []

    def test_includes_unmatched_with_default(self):
        pairs = list(iter_routed(["INFO ok"], ROUTES, default_key="other"))
        assert pairs == [("other", "INFO ok")]

    def test_empty_input_yields_nothing(self):
        assert list(iter_routed([], ROUTES)) == []

    def test_preserves_line_content(self):
        pairs = list(iter_routed(LINES, ROUTES))
        lines_out = [line for _, line in pairs]
        assert LINES[0] in lines_out
        assert LINES[3] in lines_out
