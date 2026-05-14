"""Integration tests: tagger wired into the pipeline."""

from __future__ import annotations

from io import StringIO

from logslice.tagger import compile_rules, filter_by_tag, tag_lines
from logslice.pipeline import run_pipeline
from logslice.stats import LogStats


LOG_DATA = """\
2024-01-01T00:00:01 INFO  service started
2024-01-01T00:00:02 WARN  memory at 80%
2024-01-01T00:00:03 ERROR disk full
2024-01-01T00:00:04 INFO  request handled
2024-01-01T00:00:05 ERROR timeout
"""

RULES = compile_rules({"error": r"ERROR", "warn": r"WARN", "info": r"INFO"})


def _stream():
    return StringIO(LOG_DATA)


def collect(it):
    return list(it)


class TestTaggerPipeline:
    def test_tag_then_filter_errors_only(self):
        tagged = tag_lines(_stream(), RULES)
        errors = collect(filter_by_tag(tagged, RULES, "error"))
        # tagged lines start with [error] so re-filter works
        assert len(errors) == 2
        assert all("[error]" in l for l in errors)

    def test_tag_all_lines_count(self):
        result = collect(tag_lines(_stream(), RULES))
        # 5 data lines; all have a level tag
        assert len(result) == 5

    def test_untagged_lines_pass_through(self):
        lines = ["no level here\n", "ERROR something\n"]
        result = collect(tag_lines(lines, RULES))
        assert result[0] == "no level here\n"
        assert result[1].startswith("[error]")

    def test_multi_mode_combined_tags(self):
        lines = ["ERROR WARN dual\n"]
        result = collect(tag_lines(lines, RULES, multi=True))
        assert "error" in result[0]
        assert "warn" in result[0]

    def test_pipeline_run_then_tag(self):
        stats = LogStats()
        out = StringIO()
        run_pipeline(
            source=_stream(),
            pattern=r"ERROR",
            start=None,
            end=None,
            output=out,
            stats=stats,
        )
        out.seek(0)
        tagged = collect(tag_lines(out, RULES))
        assert all("[error]" in l for l in tagged if l.strip())
