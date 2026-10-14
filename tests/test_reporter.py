"""Unit tests for the benchmark reporter module (JSON, CSV, and Markdown)."""

import csv
import json
from pathlib import Path
import tempfile
import unittest

from lib.dashboard import DashboardStats, ServiceExecutionResult
from lib.reporter import (
    export_benchmark_report,
    generate_report_filename,
    mask_phone_number,
)


class TestReporter(unittest.TestCase):
    """Test suite for benchmark report generation and formatting."""

    def setUp(self) -> None:
        self.stats = DashboardStats(
            total_tasks=3,
            completed_tasks=3,
            successful_count=2,
            failed_count=1,
            dead_proxies_count=0,
            results=[
                ServiceExecutionResult(
                    index=1,
                    service_name="divar",
                    engine="HTTP",
                    is_success=True,
                    latency_ms=120.5,
                    status_label="Success",
                    proxy_address=None,
                ),
                ServiceExecutionResult(
                    index=2,
                    service_name="snapp_food",
                    engine="HTTP",
                    is_success=True,
                    latency_ms=95.0,
                    status_label="Success",
                    proxy_address=None,
                ),
                ServiceExecutionResult(
                    index=3,
                    service_name="filimo",
                    engine="Browser",
                    is_success=False,
                    latency_ms=450.2,
                    status_label="Browser Failed",
                    proxy_address=None,
                ),
            ],
        )

    def test_mask_phone_number(self) -> None:
        """Verify middle digits masking for privacy."""
        self.assertEqual(mask_phone_number("09123456789"), "0912****789")
        self.assertEqual(mask_phone_number("123"), "123")

    def test_generate_report_filename(self) -> None:
        """Filename includes prefix and correct extension."""
        json_filename = generate_report_filename(prefix="test", extension="json")
        self.assertTrue(json_filename.startswith("test_"))
        self.assertTrue(json_filename.endswith(".json"))

        csv_filename = generate_report_filename(prefix="bench", extension=".csv")
        self.assertTrue(csv_filename.startswith("bench_"))
        self.assertTrue(csv_filename.endswith(".csv"))

    def test_export_json_report(self) -> None:
        """Verify JSON report structure and content."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = export_benchmark_report(
                stats=self.stats,
                target_phone="09123456789",
                format_type="json",
                output_directory=tmp_dir,
                rounds_executed=1,
            )
            self.assertTrue(report_path.exists())
            self.assertEqual(report_path.suffix, ".json")

            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertIn("metadata", data)
            self.assertIn("summary", data)
            self.assertIn("results", data)
            self.assertEqual(data["metadata"]["target_phone"], "0912****789")
            self.assertEqual(data["summary"]["total_requests"], 3)
            self.assertEqual(data["summary"]["successful_requests"], 2)
            self.assertEqual(data["summary"]["failed_requests"], 1)
            self.assertEqual(len(data["results"]), 3)

    def test_export_csv_report(self) -> None:
        """Verify CSV report header and rows."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = export_benchmark_report(
                stats=self.stats,
                target_phone="09123456789",
                format_type="csv",
                output_directory=tmp_dir,
                rounds_executed=2,
            )
            self.assertTrue(report_path.exists())
            self.assertEqual(report_path.suffix, ".csv")

            with open(report_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            self.assertGreaterEqual(len(rows), 4)  # Header + 3 results
            self.assertIn("service_name", rows[0])
            self.assertIn("is_success", rows[0])

    def test_export_markdown_report(self) -> None:
        """Verify Markdown report content and table formatting."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = export_benchmark_report(
                stats=self.stats,
                target_phone="09123456789",
                format_type="md",
                output_directory=tmp_dir,
                rounds_executed=1,
            )
            self.assertTrue(report_path.exists())
            self.assertEqual(report_path.suffix, ".md")

            content = report_path.read_text(encoding="utf-8")
            self.assertIn("# S-Bomber Benchmark Report", content)
            self.assertIn("0912****789", content)
            self.assertIn("divar", content)
            self.assertIn("snapp_food", content)
            self.assertIn("filimo", content)


if __name__ == "__main__":
    unittest.main()
