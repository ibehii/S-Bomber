"""Unit tests for lib/proxy_manager.py."""

import asyncio
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from lib.proxy_manager import (
    ProxyHealthResult,
    ProxyPool,
    check_proxies_health,
    load_proxies_from_file,
    normalize_proxy_address,
    prune_dead_proxies_from_file,
    test_single_proxy,
)


class TestProxyManager(unittest.TestCase):
    """Test suite for proxy normalization, file loading, pooling, and health checks."""

    def test_normalize_proxy_address(self) -> None:
        """Verify normalization of various proxy address formats."""
        self.assertEqual(normalize_proxy_address(""), "")
        self.assertEqual(normalize_proxy_address("   "), "")
        self.assertEqual(
            normalize_proxy_address("192.168.1.1:8080"),
            "http://192.168.1.1:8080",
        )
        self.assertEqual(
            normalize_proxy_address("http://192.168.1.1:8080"),
            "http://192.168.1.1:8080",
        )
        self.assertEqual(
            normalize_proxy_address("https://10.0.0.1:443"),
            "https://10.0.0.1:443",
        )
        self.assertEqual(
            normalize_proxy_address("socks5://user:pass@127.0.0.1:1080"),
            "socks5://user:pass@127.0.0.1:1080",
        )

    def test_load_proxies_from_file(self) -> None:
        """Loading proxies ignores comments, blanks, and deduplicates."""
        file_content = """# Comment line
192.168.1.1:8080

# Another comment
http://192.168.1.2:8080
192.168.1.1:8080
socks5://10.0.0.1:1080
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = Path(tmp_file.name)

        try:
            loaded = load_proxies_from_file(tmp_path)
            self.assertEqual(len(loaded), 3)
            self.assertIn("http://192.168.1.1:8080", loaded)
            self.assertIn("http://192.168.1.2:8080", loaded)
            self.assertIn("socks5://10.0.0.1:1080", loaded)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_load_proxies_from_nonexistent_file(self) -> None:
        """Non-existent proxy file returns empty list."""
        self.assertEqual(load_proxies_from_file("/invalid/path/proxies.txt"), [])

    def test_proxy_pool_round_robin_and_lifecycle(self) -> None:
        """Verify round-robin cycling, total count, and dead proxy tracking."""
        proxies = ["http://proxy1:80", "http://proxy2:80", "http://proxy3:80"]
        pool = ProxyPool(proxies)

        self.assertTrue(pool.has_proxies)
        self.assertEqual(pool.total_count, 3)

        # Round robin cycling
        self.assertEqual(pool.get_next_proxy(), "http://proxy1:80")
        self.assertEqual(pool.get_next_proxy(), "http://proxy2:80")
        self.assertEqual(pool.get_next_proxy(), "http://proxy3:80")
        self.assertEqual(pool.get_next_proxy(), "http://proxy1:80")

        # Record dead proxy
        pool.record_dead_proxy("http://proxy2:80")
        self.assertIn("http://proxy2:80", pool.dead_proxies)

        # Format requests proxy dict
        formatted = ProxyPool.format_requests_proxy_dictionary("http://proxy1:80")
        self.assertEqual(formatted, {"http": "http://proxy1:80", "https": "http://proxy1:80"})

    def test_empty_proxy_pool(self) -> None:
        """Empty pool handles next calls gracefully."""
        pool = ProxyPool([])
        self.assertFalse(pool.has_proxies)
        self.assertEqual(pool.total_count, 0)
        self.assertIsNone(pool.get_next_proxy())

    def test_prune_dead_proxies_from_file(self) -> None:
        """Pruning removes dead proxies while preserving comments and alive ones."""
        initial_content = """# Header comment
192.168.1.1:8080
192.168.1.2:8080
# Mid comment
192.168.1.3:8080
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp_file:
            tmp_file.write(initial_content)
            tmp_path = Path(tmp_file.name)

        try:
            dead = {"http://192.168.1.2:8080"}
            removed_count = prune_dead_proxies_from_file(tmp_path, dead)
            self.assertEqual(removed_count, 1)

            surviving = tmp_path.read_text(encoding="utf-8")
            self.assertIn("# Header comment", surviving)
            self.assertIn("192.168.1.1:8080", surviving)
            self.assertIn("192.168.1.3:8080", surviving)
            self.assertNotIn("192.168.1.2:8080", surviving)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_prune_nonexistent_file_returns_zero(self) -> None:
        """Pruning a missing file returns 0."""
        self.assertEqual(prune_dead_proxies_from_file("/missing/proxy.txt", {"http://1.1.1.1"}), 0)

    def test_test_single_proxy_invalid_host(self) -> None:
        """Invalid proxy host returns failed health result."""
        result = asyncio.run(test_single_proxy("http://", timeout_seconds=1.0))
        self.assertFalse(result.is_alive)
        self.assertEqual(result.error_message, "Invalid proxy hostname")

    @patch("asyncio.open_connection")
    def test_test_single_proxy_success(self, mock_open_connection: AsyncMock) -> None:
        """Mock successful TCP connection to proxy."""
        mock_writer = MagicMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()
        mock_reader = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)

        result = asyncio.run(test_single_proxy("http://1.2.3.4:8080", timeout_seconds=2.0))
        self.assertTrue(result.is_alive)
        self.assertGreaterEqual(result.latency_ms, 0.0)
        self.assertIsNone(result.error_message)

    @patch("asyncio.open_connection", side_effect=asyncio.TimeoutError)
    def test_test_single_proxy_timeout(self, mock_open_connection: AsyncMock) -> None:
        """Connection timeout marks proxy as dead."""
        result = asyncio.run(test_single_proxy("http://1.2.3.4:8080", timeout_seconds=0.1))
        self.assertFalse(result.is_alive)
        self.assertEqual(result.error_message, "Connection timed out")

    @patch("asyncio.open_connection")
    def test_check_proxies_health_concurrent(self, mock_open_connection: AsyncMock) -> None:
        """Concurrent health check verifies multiple proxies."""
        mock_writer = MagicMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()
        mock_reader = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)

        proxies = ["http://1.1.1.1:80", "http://2.2.2.2:80"]
        results = asyncio.run(check_proxies_health(proxies, max_concurrency=5, timeout_seconds=1.0))
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.is_alive for r in results))


if __name__ == "__main__":
    unittest.main()
