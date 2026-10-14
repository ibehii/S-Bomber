"""Unit tests for Click-based CLI using Click's CliRunner."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from lib.cli import cli


class TestClickCLI(unittest.TestCase):
    """Test suite for Click command-line interface arguments, options, and subcommands."""

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_cli_help_flag(self) -> None:
        """Verify --help flag outputs usage and options."""
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("S-Bomber", result.output)
        self.assertIn("--phone", result.output)
        self.assertIn("--interval", result.output)
        self.assertIn("--driver", result.output)
        self.assertIn("--services", result.output)
        self.assertIn("--only-browser", result.output)
        self.assertIn("--no-browser", result.output)
        self.assertIn("check-proxies", result.output)

    def test_phone_option_execution(self) -> None:
        """Verify --phone option is accepted and processed."""
        result = self.runner.invoke(cli, ["--phone", "09123456789"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Target phone: 09123456789", result.output)

    def test_interval_and_timeout_options(self) -> None:
        """Verify custom --interval and --timeout options."""
        result = self.runner.invoke(
            cli,
            ["-p", "09123456789", "-i", "2.5", "-t", "15.0"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Interval: 2.5s", result.output)
        self.assertIn("Timeout: 15.0s", result.output)

    def test_driver_selection(self) -> None:
        """Verify --driver accepts valid choice chrome and firefox."""
        result_chrome = self.runner.invoke(cli, ["-p", "09123456789", "--driver", "chrome"])
        self.assertEqual(result_chrome.exit_code, 0)
        self.assertIn("Driver: chrome", result_chrome.output)

        result_firefox = self.runner.invoke(cli, ["-p", "09123456789", "--driver", "firefox"])
        self.assertEqual(result_firefox.exit_code, 0)
        self.assertIn("Driver: firefox", result_firefox.output)

        result_invalid = self.runner.invoke(cli, ["-p", "09123456789", "--driver", "safari"])
        self.assertNotEqual(result_invalid.exit_code, 0)
        self.assertIn("Invalid value for '-d' / '--driver'", result_invalid.output)

    def test_services_filtering_option(self) -> None:
        """Verify --services parses comma-separated service names."""
        result = self.runner.invoke(
            cli,
            ["-p", "09123456789", "--services", "divar,digikala,snapp_food"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Filtered services: divar, digikala, snapp_food", result.output)

    def test_only_browser_and_no_browser_flags(self) -> None:
        """Verify exclusive browser mode flags."""
        result_only = self.runner.invoke(cli, ["-p", "09123456789", "--only-browser"])
        self.assertEqual(result_only.exit_code, 0)
        self.assertIn("Mode: Only browser automation", result_only.output)

        result_no = self.runner.invoke(cli, ["-p", "09123456789", "--no-browser"])
        self.assertEqual(result_no.exit_code, 0)
        self.assertIn("Mode: Only HTTP API services", result_no.output)

    def test_headless_flags(self) -> None:
        """Verify --headless and --no-headless toggles."""
        result_headless = self.runner.invoke(cli, ["-p", "09123456789", "--headless"])
        self.assertEqual(result_headless.exit_code, 0)
        self.assertIn("Headless: True", result_headless.output)

        result_no_headless = self.runner.invoke(cli, ["-p", "09123456789", "--no-headless"])
        self.assertEqual(result_no_headless.exit_code, 0)
        self.assertIn("Headless: False", result_no_headless.output)

    def test_rich_dashboard_flags(self) -> None:
        """Verify --rich and --no-rich toggles in CLI options."""
        result_rich = self.runner.invoke(cli, ["-p", "09123456789", "--rich"])
        self.assertEqual(result_rich.exit_code, 0)

        result_no_rich = self.runner.invoke(cli, ["-p", "09123456789", "--no-rich"])
        self.assertEqual(result_no_rich.exit_code, 0)

    def test_check_proxies_subcommand_empty_file(self) -> None:
        """Verify check-proxies subcommand handles empty or missing proxy file."""
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            result = self.runner.invoke(cli, ["check-proxies", "--proxy-file", str(tmp_path)])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No proxies found", result.output)
        finally:
            tmp_path.unlink(missing_ok=True)

    @patch("lib.cli.check_proxies_health")
    def test_check_proxies_subcommand_with_proxies(self, mock_check_health) -> None:
        """Verify check-proxies subcommand tests proxies and reports results."""
        from lib.proxy_manager import ProxyHealthResult

        mock_check_health.return_value = [
            ProxyHealthResult(proxy_address="http://1.1.1.1:80", is_alive=True, latency_ms=45.2),
            ProxyHealthResult(
                proxy_address="http://2.2.2.2:80",
                is_alive=False,
                latency_ms=0.0,
                error_message="Timed out",
            ),
        ]

        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
            tmp_file.write("1.1.1.1:80\n2.2.2.2:80\n")
            tmp_path = Path(tmp_file.name)

        try:
            result = self.runner.invoke(
                cli,
                ["check-proxies", "--proxy-file", str(tmp_path), "--prune"],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ALIVE", result.output)
            self.assertIn("DEAD", result.output)
            self.assertIn("1/2 proxies alive", result.output)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_interactive_menu_exit_option(self) -> None:
        """Verify interactive menu exit choice 4 exits cleanly."""
        result = self.runner.invoke(cli, [], input="4\n")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Exiting S-Bomber.", result.output)

    def test_tags_option(self) -> None:
        """Verify --tags option filters services according to category."""
        result = self.runner.invoke(cli, ["-p", "09123456789", "-g", "food"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Filter tags: food", result.output)
        self.assertIn("snapp_food", result.output)

    def test_export_options(self) -> None:
        """Verify --export and --export-format options are processed."""
        result = self.runner.invoke(
            cli,
            ["-p", "09123456789", "--export", "--export-format", "csv", "--reports-dir", "custom_reports"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Export report: True", result.output)
        self.assertIn("format=csv", result.output)
        self.assertIn("dir=custom_reports", result.output)

    def test_rounds_options(self) -> None:
        """Verify -r / --rounds and --round-interval options."""
        result = self.runner.invoke(
            cli,
            ["-p", "09123456789", "-r", "3", "--round-interval", "2.0"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Rounds: 3", result.output)
        self.assertIn("Round Interval: 2.0s", result.output)

    @patch("lib.cli.check_all_services")
    def test_check_services_subcommand(self, mock_check_services) -> None:
        """Verify check-services subcommand probes endpoints and prints report."""
        from lib.service_checker import ServiceHealthResult

        mock_check_services.return_value = [
            ServiceHealthResult(
                service_name="divar",
                endpoint_url="https://api.divar.ir",
                is_reachable=True,
                status_code=200,
                latency_ms=32.4,
            ),
            ServiceHealthResult(
                service_name="snapp_offline",
                endpoint_url="https://offline.snapp.ir",
                is_reachable=False,
                status_code=None,
                latency_ms=0.0,
                error_message="Host unreachable",
            ),
        ]

        result = self.runner.invoke(cli, ["check-services", "-t", "2.0"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("divar", result.output)
        self.assertIn("ONLINE", result.output)
        self.assertIn("snapp_offline", result.output)
        self.assertIn("OFFLINE", result.output)
        self.assertIn("1/2 online", result.output)

    @patch("lib.cli.update_proxy_file_with_live_proxies")
    def test_update_proxies_subcommand(self, mock_update_proxies) -> None:
        """Verify update-proxies subcommand triggers proxy scraping and reports live nodes."""
        from lib.proxy_manager import ProxyHealthResult

        mock_update_proxies.return_value = [
            ProxyHealthResult(proxy_address="http://5.5.5.5:8080", is_alive=True, latency_ms=42.1),
        ]

        result = self.runner.invoke(cli, ["update-proxies", "-m", "10", "-t", "2.0"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("5.5.5.5:8080", result.output)
        self.assertIn("Successfully discovered and saved 1 live proxies", result.output)


if __name__ == "__main__":
    unittest.main()

