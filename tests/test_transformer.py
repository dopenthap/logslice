"""Tests for logslice.transformer."""

import pytest
from logslice.transformer import (
    extract_field,
    parse_kv,
    replace_field,
    make_transformer,
    transform_lines,
)


# ---------------------------------------------------------------------------
# extract_field
# ---------------------------------------------------------------------------

class TestExtractField:
    def test_first_field(self):
        assert extract_field("a b c", 0) == "a"

    def test_last_field(self):
        assert extract_field("a b c", 2) == "c"

    def test_out_of_range_returns_none(self):
        assert extract_field("a b", 5) is None

    def test_negative_index_returns_none(self):
        assert extract_field("a b c", -1) is None

    def test_custom_separator(self):
        assert extract_field("a,b,c", 1, sep=",") == "b"

    def test_trailing_newline_stripped(self):
        assert extract_field("hello world\n", 1) == "world"


# ---------------------------------------------------------------------------
# parse_kv
# ---------------------------------------------------------------------------

class TestParseKv:
    def test_simple_pairs(self):
        result = parse_kv("status=200 method=GET path=/index")
        assert result == {"status": "200", "method": "GET", "path": "/index"}

    def test_empty_string(self):
        assert parse_kv("") == {}

    def test_no_pairs(self):
        assert parse_kv("plain log line without kv") == {}

    def test_quoted_value(self):
        result = parse_kv('msg="hello world" level=info')
        assert result["level"] == "info"


# ---------------------------------------------------------------------------
# replace_field
# ---------------------------------------------------------------------------

class TestReplaceField:
    def test_simple_replacement(self):
        assert replace_field("foo bar foo", "foo", "baz") == "baz bar baz"

    def test_count_limits_replacements(self):
        assert replace_field("foo foo foo", "foo", "x", count=1) == "x foo foo"

    def test_preserves_trailing_newline(self):
        result = replace_field("hello world\n", "world", "there")
        assert result == "hello there\n"

    def test_no_match_unchanged(self):
        assert replace_field("abc", "xyz", "!") == "abc"


# ---------------------------------------------------------------------------
# make_transformer / transform_lines
# ---------------------------------------------------------------------------

class TestMakeTransformer:
    def test_none_pattern_is_noop(self):
        t = make_transformer()
        assert t("unchanged") == "unchanged"

    def test_with_pattern(self):
        t = make_transformer(pattern=r"\d+", replacement="NUM")
        assert t("error 404 on line 12") == "error NUM on line NUM"

    def test_count_respected(self):
        t = make_transformer(pattern=r"\d+", replacement="NUM", count=1)
        assert t("404 500") == "NUM 500"


class TestTransformLines:
    def test_applies_to_all_lines(self):
        lines = ["foo\n", "foo bar\n", "baz\n"]
        t = make_transformer(pattern="foo", replacement="qux")
        result = list(transform_lines(lines, t))
        assert result == ["qux\n", "qux bar\n", "baz\n"]

    def test_empty_input(self):
        result = list(transform_lines([], make_transformer()))
        assert result == []

    def test_noop_transformer_unchanged(self):
        lines = ["a\n", "b\n"]
        result = list(transform_lines(lines, make_transformer()))
        assert result == lines
