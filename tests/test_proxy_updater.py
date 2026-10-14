"""Unit tests for public proxy scraper and automated updater."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from lib.proxy_manager import ProxyHealthResult
from lib.proxy_updater import (
    fetch_all_public_proxies,
    fetch_raw_proxies_from_source,
    update_proxy_file_with_live_proxies,
)


class TestProxyUpdater(unittest.TestCase):
    """Test suite for scraping public proxies and updating proxy list."""

    @patch("requests.get")
    def test_fetch_raw_proxies_from_source(self, mock_get: MagicMock) -> None:
        """Parse IP:PORT occurrences from HTTP response."""
        mock_response = MagicMock()
        mock_response.text = "1.2.3.4:8080\n5.6.7.8:3128\nsome extra text 9.10.11.12:80"
        mock_get.return_value = mock_response

        found = fetch_raw_proxies_from_source("https://example.com/proxies.txt")
        self.assertEqual(len(found), 3)
        self.assertIn("1.2.3.4:8080", found)
        self.assertIn("5.6.7.8:3128", found)
        self.assertIn("9.10.11.12:80", found)

    @patch("requests.get")
    def test_fetch_raw_proxies_network_failure(self, mock_get: MagicMock) -> None:
        """Network error gracefully returns empty list."""
        mock_get.side_effect = Exception("DNS lookup failure")
        found = fetch_raw_proxies_from_source("https://broken.source.url")
        self.assertEqual(found, [])

    @patch("lib.proxy_updater.fetch_raw_proxies_from_source")
    def test_fetch_all_public_proxies_deduplication(
        self,
        mock_fetch_source: MagicMock,
    ) -> None:
        """Candidate proxies from multiple sources are deduplicated."""
        mock_fetch_source.side_effect = [
            ["1.1.1.1:80", "2.2.2.2:8080"],
            ["2.2.2.2:8080", "3.3.3.3:3128"],
        ]

        candidates = fetch_all_public_proxies(
            sources=["http://source1.com", "http://source2.com"],
            max_candidates=10,
        )
        self.assertEqual(len(candidates), 3)

    @patch("lib.proxy_updater.fetch_all_public_proxies")
    @patch("lib.proxy_updater.check_proxies_health")
    def test_update_proxy_file_with_live_proxies(
        self,
        mock_check_health: MagicMock,
        mock_fetch_all: MagicMock,
    ) -> None:
        """Live proxies are sorted by latency and written to destination file."""
        mock_fetch_all.return_value = ["1.1.1.1:80", "2.2.2.2:80", "3.3.3.3:80"]
        mock_check_health.return_value = [
            ProxyHealthResult(proxy_address="http://2.2.2.2:80", is_alive=True, latency_ms=150.0),
            ProxyHealthResult(proxy_address="http://1.1.1.1:80", is_alive=True, latency_ms=50.0),
            ProxyHealthResult(proxy_address="http://3.3.3.3:80", is_alive=False, latency_ms=0.0),
        ]

        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            live_results = update_proxy_file_with_live_proxies(
                destination_file=tmp_path,
                max_working_proxies=10,
                timeout_seconds=2.0,
            )
            self.assertEqual(len(live_results), 2)
            # Verify sorted by latency
            self.assertEqual(live_results[0].proxy_address, "http://1.1.1.1:80")
            self.assertEqual(live_results[1].proxy_address, "http://2.2.2.2:80")

            file_content = tmp_path.read_text(encoding="utf-8")
            self.assertIn("1.1.1.1:80", file_content)
            self.assertIn("2.2.2.2:80", file_content)
            self.assertNotIn("3.3.3.3:80", file_content)
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
