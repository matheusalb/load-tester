"""Export load test metrics to various formats."""
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class MetricsExporter:
    """Export load test metrics to various formats."""

    def __init__(self, statistics: dict[str, Any]) -> None:
        """Initialize the metrics exporter.

        Args:
            statistics: The statistics dictionary from a load test.

        """
        self.statistics = statistics
        self.timestamp = datetime.now().isoformat()

    def to_json(self, output_path: str) -> None:
        """Export metrics to JSON format.

        Args:
            output_path: Path where the JSON file will be written.

        """
        export_data = {"timestamp": self.timestamp, "metrics": self.statistics}

        with Path(output_path).open("w") as f:
            json.dump(export_data, f, indent=2)

    def to_csv(self, output_path: str) -> None:
        """Export metrics to CSV format.

        Args:
            output_path: Path where the CSV file will be written.

        """
        # Flatten nested metrics for CSV
        flat_metrics = {"timestamp": self.timestamp, **self.statistics}

        with Path(output_path).open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(flat_metrics.keys())
            writer.writerow(flat_metrics.values())


def export_metrics(metrics: dict[str, Any], format_type: str, output_path: str) -> None:
    """Export metrics in specified format.

    Args:
        metrics: The statistics dictionary from a load test.
        format_type: The export format (json, csv).
        output_path: Path where the output file will be written.

    """
    exporter = MetricsExporter(metrics)

    if format_type == "json":
        exporter.to_json(output_path)
    elif format_type == "csv":
        exporter.to_csv(output_path)
    else:
        msg = f"Unsupported export format: {format_type}"
        raise ValueError(msg)

    print(f"Metrics exported to {output_path} in {format_type} format")
