"""Unit tests for the export module."""

from pathlib import Path

from ccload.exporters.metric_exporter import MetricsExporter, export_metrics
from tests.unit.utils import assert_values

statistics = {
    "total_requests": 10,
    "successful_requests": 8,
    "failed_requests": 2,
    "request_time_min": 0.1,
    "request_time_max": 1.0,
    "request_time_mean": 0.5,
    "ttfb_min": 0.2,
    "ttfb_max": 0.8,
    "ttfb_mean": 0.5,
    "ttlb_min": 0.3,
    "ttlb_max": 0.7,
    "ttlb_mean": 0.5,
    "requests_per_second": 2.0,
}

def test_metrics_exporter(tmp_path: Path) -> None:
    """Test the MetricsExporter class."""
    exporter = MetricsExporter(statistics)
    exporter.to_json(str(tmp_path / "test.json"))
    exporter.to_csv(str(tmp_path / "test.csv"))
    assert_values(
        (tmp_path / "test.json").exists(),
        value2=True,
        msg="JSON file not created",
    )
    assert_values(
        (tmp_path / "test.csv").exists(),
        value2=True,
        msg="CSV file not created",
    )

def test_export_metrics(tmp_path: Path) -> None:
    """Test the export_metrics function."""
    export_metrics(statistics, "json", str(tmp_path / "test.json"))
    export_metrics(statistics, "csv", str(tmp_path / "test.csv"))
    assert_values(
        (tmp_path / "test.json").exists(),
        value2=True,
        msg="JSON file not created",
    )
    assert_values(
        (tmp_path / "test.csv").exists(),
        value2=True,
        msg="CSV file not created",
    )
