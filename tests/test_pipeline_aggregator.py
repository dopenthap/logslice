"""Integration tests: aggregator used after pipeline filtering."""

from __future__ import annotations

from io import StringIO

from logslice.aggregator import aggregate_by, count_by, top_keys
from logslice.pipeline import run_pipeline
from logslice.stats import LogStats


LOG_LINES = [
    "2024-01-01T00:00:01 ERROR disk full\n",
    "2024-01-01T00:00:02 INFO  service started\n",
    "2024-01-01T00:00:03 ERROR timeout\n",
    "2024-01-01T00:00:04 WARN  high memory\n",
    "2024-01-01T00:00:05 ERROR connection refused\n",
    "2024-01-01T00:00:06 INFO  request ok\n",
]


def _level(line: str) -> str | None:
    parts = line.split()
    return parts[1].strip() if len(parts) >= 2 else None


def _make_stream() -> StringIO:
    return StringIO("".join(LOG_LINES))


def _collect_pipeline(**kwargs):
    stats = LogStats()
    stream = _make_stream()
    return list(run_pipeline(stream, stats, **kwargs)), stats


class TestPipelineAggregator:
    def test_aggregate_all_lines_by_level(self):
        lines, _ = _collect_pipeline()
        buckets = aggregate_by(lines, _level)
        assert len(buckets["ERROR"]) == 3
        assert len(buckets["INFO"]) == 2
        assert len(buckets["WARN"]) == 1

    def test_count_after_pattern_filter(self):
        lines, _ = _collect_pipeline(pattern="ERROR")
        counts = count_by(lines, _level)
        assert counts.get("ERROR") == 3
        assert "INFO" not in counts

    def test_top_keys_reflects_most_common_level(self):
        lines, _ = _collect_pipeline()
        counts = count_by(lines, _level)
        top = top_keys(counts, n=1)
        assert top[0][0] == "ERROR"
        assert top[0][1] == 3

    def test_aggregate_empty_pipeline_result(self):
        lines, _ = _collect_pipeline(pattern="CRITICAL")
        buckets = aggregate_by(lines, _level)
        assert buckets == {}

    def test_unkeyed_bucket_not_present_for_well_formed_logs(self):
        lines, _ = _collect_pipeline()
        buckets = aggregate_by(lines, _level)
        assert "__unkeyed__" not in buckets
