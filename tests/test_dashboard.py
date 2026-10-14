"""Unit tests for lib/dashboard.py (DispatchDashboard)."""

import io
import unittest
from unittest.mock import MagicMock, patch

from lib.dashboard import (
    DashboardStats,
    DispatchDashboard,
    RICH_AVAILABLE,
    ServiceExecutionResult,
)


class TestDashboardStats(unittest.TestCase):
    """Test metrics and statistics calculation in DashboardStats."""

    def test_empty_stats_averages(self) -> None:
        """Verify that zero completed tasks return 0.0 for averages and rates."""
        stats = DashboardStats(total_tasks=10)
        self.assertEqual(stats.average_latency_ms, 0.0)
        self.assertEqual(stats.success_percentage, 0.0)

    def test_stats_aggregation(self) -> None:
        """Verify latency summation and success percentage calculation."""
        stats = DashboardStats(
            total_tasks=4,
            completed_tasks=4,
            successful_count=3,
            failed_count=1,
            total_latency_ms=400.0,
            dead_proxies_count=1,
        )
        self.assertAlmostEqual(stats.average_latency_ms, 100.0)
        self.assertAlmostEqual(stats.success_percentage, 75.0)


class TestDispatchDashboard(unittest.TestCase):
    """Test suite for DispatchDashboard execution, fallback, and rendering."""

    def test_initialization_fallback_mode(self) -> None:
        """Dashboard initialized with use_rich=False operates in fallback mode."""
        dashboard = DispatchDashboard(total_tasks=5, use_rich=False)
        self.assertFalse(dashboard.is_rich_active)
        self.assertIsNone(dashboard.live)

    def test_record_results_and_stats_fallback(self) -> None:
        """Recording results in fallback mode updates stats and outputs cleanly."""
        dashboard = DispatchDashboard(total_tasks=2, use_rich=False)

        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            dashboard.record_result(
                service_name="divar",
                engine="HTTP",
                is_success=True,
                latency_ms=120.5,
                status_label="Success",
                proxy="http://1.2.3.4:8080",
            )
            dashboard.record_result(
                service_name="snapp_food",
                engine="Browser",
                is_success=False,
                latency_ms=350.0,
                status_label="Rejected",
                proxy=None,
            )

        self.assertEqual(dashboard.stats.completed_tasks, 2)
        self.assertEqual(dashboard.stats.successful_count, 1)
        self.assertEqual(dashboard.stats.failed_count, 1)
        self.assertAlmostEqual(dashboard.stats.average_latency_ms, 235.25)
        self.assertEqual(len(dashboard.stats.results), 2)

    def test_record_dead_proxy_increments_counter(self) -> None:
        """Recording dead proxies updates internal counter."""
        dashboard = DispatchDashboard(total_tasks=5, use_rich=False)
        dashboard.record_dead_proxy()
        dashboard.record_dead_proxy()
        self.assertEqual(dashboard.stats.dead_proxies_count, 2)

    def test_context_manager_lifecycle_fallback(self) -> None:
        """Context manager lifecycle executes cleanly without exceptions."""
        with DispatchDashboard(total_tasks=3, use_rich=False) as dashboard:
            dashboard.record_result("tapsi", "HTTP", True, 50.0)
        self.assertEqual(dashboard.stats.completed_tasks, 1)

    def test_render_summary_fallback(self) -> None:
        """Summary rendering in fallback mode prints expected summary block."""
        dashboard = DispatchDashboard(total_tasks=1, use_rich=False)
        dashboard.record_result("divar", "HTTP", True, 100.0)

        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            dashboard.render_summary()
            summary_output = fake_stdout.getvalue()

        self.assertIn("DISPATCH OPERATION SUMMARY", summary_output)
        self.assertIn("Total Requests Dispatched: 1", summary_output)
        self.assertIn("Successful: 1", summary_output)

    @patch("lib.dashboard.RICH_AVAILABLE", True)
    @patch("lib.dashboard.sys.stdout.isatty", return_value=True)
    @patch("lib.dashboard.Console")
    @patch("lib.dashboard.Progress")
    @patch("lib.dashboard.SpinnerColumn")
    @patch("lib.dashboard.TextColumn")
    @patch("lib.dashboard.BarColumn")
    @patch("lib.dashboard.TimeElapsedColumn")
    @patch("lib.dashboard.TimeRemainingColumn")
    def test_rich_initialization_when_available(
        self,
        mock_time_rem: MagicMock,
        mock_time_el: MagicMock,
        mock_bar: MagicMock,
        mock_text: MagicMock,
        mock_spinner: MagicMock,
        mock_progress_cls: MagicMock,
        mock_console_cls: MagicMock,
        mock_isatty: MagicMock,
    ) -> None:
        """When rich is available and stdout is TTY, rich mode activates."""
        mock_progress_instance = MagicMock()
        mock_progress_cls.return_value = mock_progress_instance

        dashboard = DispatchDashboard(total_tasks=5, use_rich=True)
        self.assertTrue(dashboard.is_rich_active)
        mock_progress_instance.add_task.assert_called_once()


if __name__ == "__main__":
    unittest.main()
