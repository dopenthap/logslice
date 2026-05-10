"""Integration tests: router + splitter wired into the pipeline."""

import io
from logslice.router import route_lines, iter_routed
from logslice.splitter import split_to_buffers


def _level(line: str) -> str:
    for lvl in ("ERROR", "WARN", "INFO", "DEBUG"):
        if lvl in line:
            return lvl
    return "OTHER"


ROUTES = [
    ("error", lambda l: "ERROR" in l),
    ("warn", lambda l: "WARN" in l),
    ("info", lambda l: "INFO" in l),
]

LOG_STREAM = [
    "2024-06-01T10:00:00 ERROR connection refused\n",
    "2024-06-01T10:00:01 WARN retry attempt 1\n",
    "2024-06-01T10:00:02 INFO request received\n",
    "2024-06-01T10:00:03 ERROR timeout\n",
    "2024-06-01T10:00:04 DEBUG verbose detail\n",
    "2024-06-01T10:00:05 INFO response sent\n",
]


class TestRouterPipelineIntegration:
    def test_all_levels_partitioned_correctly(self):
        result = route_lines(LOG_STREAM, ROUTES, default_key="other")
        assert len(result["error"]) == 2
        assert len(result["warn"]) == 1
        assert len(result["info"]) == 2
        assert len(result["other"]) == 1

    def test_iter_routed_preserves_order_within_bucket(self):
        pairs = list(iter_routed(LOG_STREAM, ROUTES))
        error_lines = [l for k, l in pairs if k == "error"]
        assert "connection refused" in error_lines[0]
        assert "timeout" in error_lines[1]

    def test_split_to_buffers_full_pipeline(self):
        buffers, counts = split_to_buffers(LOG_STREAM, ROUTES, default_key="other")
        assert counts["error"] == 2
        assert counts["warn"] == 1
        assert counts["info"] == 2
        assert counts["other"] == 1

    def test_buffer_content_readable(self):
        buffers, _ = split_to_buffers(LOG_STREAM, ROUTES)
        error_content = buffers["error"].read()
        assert "connection refused" in error_content
        assert "timeout" in error_content
        assert "WARN" not in error_content

    def test_no_cross_contamination_between_buckets(self):
        buffers, _ = split_to_buffers(LOG_STREAM, ROUTES, default_key="other")
        warn_content = buffers["warn"].read()
        assert "ERROR" not in warn_content
        assert "INFO" not in warn_content
