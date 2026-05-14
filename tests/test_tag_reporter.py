"""Tests for logslice.tag_reporter."""

from __future__ import annotations

import json
from collections import Counter
from io import StringIO

import pytest

from logslice.tagger import compile_rules
from logslice.tag_reporter import (
    count_tags,
    format_tag_report_json,
    format_tag_report_plain,
    write_tag_report,
)


RULES = compile_rules({"error": r"ERROR", "warn": r"WARN", "info": r"INFO"})

LINES = [
    "ERROR bad\n",
    "WARN low\n",
    "INFO ok\n",
    "INFO startup\n",
    "ERROR timeout\n",
    "DEBUG verbose\n",
]


class TestCountTags:
    def test_basic_counts(self):
        c = count_tags(LINES, RULES)
        assert c["error"] == 2
        assert c["warn"] == 1
        assert c["info"] == 2

    def test_untagged_not_counted(self):
        c = count_tags(LINES, RULES)
        assert "debug" not in c

    def test_empty_input_returns_empty_counter(self):
        c = count_tags([], RULES)
        assert len(c) == 0

    def test_multi_mode_counts_all_tags(self):
        lines = ["ERROR WARN both\n"]
        c = count_tags(lines, RULES, multi=True)
        assert c["error"] == 1
        assert c["warn"] == 1

    def test_single_mode_first_tag_only(self):
        lines = ["ERROR WARN both\n"]
        c = count_tags(lines, RULES, multi=False)
        assert c["error"] == 1
        assert "warn" not in c


class TestFormatPlain:
    def test_contains_tag_labels(self):
        c = Counter({"error": 3, "info": 1})
        report = format_tag_report_plain(c)
        assert "error" in report
        assert "info" in report

    def test_contains_total(self):
        c = Counter({"error": 3, "info": 1})
        report = format_tag_report_plain(c)
        assert "total" in report
        assert "4" in report

    def test_empty_counter_message(self):
        report = format_tag_report_plain(Counter())
        assert "no tags" in report

    def test_percentage_present(self):
        c = Counter({"error": 1, "info": 1})
        report = format_tag_report_plain(c)
        assert "%" in report


class TestFormatJson:
    def test_valid_json(self):
        c = Counter({"error": 2, "warn": 1})
        payload = json.loads(format_tag_report_json(c))
        assert payload["total"] == 3
        assert payload["tags"]["error"] == 2

    def test_empty_counter(self):
        payload = json.loads(format_tag_report_json(Counter()))
        assert payload["total"] == 0
        assert payload["tags"] == {}


class TestWriteTagReport:
    def test_plain_written_to_stream(self):
        out = StringIO()
        write_tag_report(Counter({"error": 1}), out, fmt="plain")
        assert "error" in out.getvalue()

    def test_json_written_to_stream(self):
        out = StringIO()
        write_tag_report(Counter({"error": 1}), out, fmt="json")
        payload = json.loads(out.getvalue())
        assert payload["tags"]["error"] == 1

    def test_default_format_is_plain(self):
        out = StringIO()
        write_tag_report(Counter({"warn": 2}), out)
        assert "warn" in out.getvalue()
        assert out.getvalue().startswith("tag counts")
