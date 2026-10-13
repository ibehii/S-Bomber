"""Tests for cross-platform geckodriver resolution logic."""

from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from Bomber import resolve_and_download_geckodriver


class TestGeckodriverResolution(unittest.TestCase):
    """Verify cross-platform resolution mapping for geckodriver downloads."""

    @patch("platform.system", return_value="Linux")
    @patch("platform.machine", return_value="x86_64")
    @patch("builtins.print")
    @patch("requests.get")
    def test_linux_x86_64_resolution(
        self,
        mock_requests_get: MagicMock,
        mock_builtin_print: MagicMock,
        mock_platform_machine: MagicMock,
        mock_platform_system: MagicMock,
    ) -> None:
        mock_network_response: MagicMock = MagicMock(status_code=404)
        mock_network_response.raise_for_status.side_effect = Exception("Mocked abort")
        mock_requests_get.return_value = mock_network_response

        dummy_target_directory: Path = Path("/tmp")
        resolve_and_download_geckodriver(dummy_target_directory)

        target_request_url: str = mock_requests_get.call_args[0][0]
        self.assertIn("linux64.tar.gz", target_request_url)

    @patch("platform.system", return_value="Darwin")
    @patch("platform.machine", return_value="arm64")
    @patch("builtins.print")
    @patch("requests.get")
    def test_macos_arm64_resolution(
        self,
        mock_requests_get: MagicMock,
        mock_builtin_print: MagicMock,
        mock_platform_machine: MagicMock,
        mock_platform_system: MagicMock,
    ) -> None:
        mock_network_response: MagicMock = MagicMock(status_code=404)
        mock_network_response.raise_for_status.side_effect = Exception("Mocked abort")
        mock_requests_get.return_value = mock_network_response

        dummy_target_directory: Path = Path("/tmp")
        resolve_and_download_geckodriver(dummy_target_directory)

        target_request_url: str = mock_requests_get.call_args[0][0]
        self.assertIn("macos-aarch64.tar.gz", target_request_url)

    @patch("platform.system", return_value="Windows")
    @patch("platform.machine", return_value="AMD64")
    @patch("builtins.print")
    @patch("requests.get")
    def test_windows_amd64_resolution(
        self,
        mock_requests_get: MagicMock,
        mock_builtin_print: MagicMock,
        mock_platform_machine: MagicMock,
        mock_platform_system: MagicMock,
    ) -> None:
        mock_network_response: MagicMock = MagicMock(status_code=404)
        mock_network_response.raise_for_status.side_effect = Exception("Mocked abort")
        mock_requests_get.return_value = mock_network_response

        dummy_target_directory: Path = Path("/tmp")
        resolve_and_download_geckodriver(dummy_target_directory)

        target_request_url: str = mock_requests_get.call_args[0][0]
        self.assertIn("win64.zip", target_request_url)

    @patch("platform.system", return_value="Linux")
    @patch("platform.machine", return_value="aarch64")
    @patch("builtins.print")
    @patch("requests.get")
    def test_linux_arm64_aarch64_resolution(
        self,
        mock_requests_get: MagicMock,
        mock_builtin_print: MagicMock,
        mock_platform_machine: MagicMock,
        mock_platform_system: MagicMock,
    ) -> None:
        """Regression test: Linux systems reporting 'aarch64' must download linux-aarch64 archive."""
        mock_network_response: MagicMock = MagicMock(status_code=404)
        mock_network_response.raise_for_status.side_effect = Exception("Mocked abort")
        mock_requests_get.return_value = mock_network_response

        dummy_target_directory: Path = Path("/tmp")
        resolve_and_download_geckodriver(dummy_target_directory)

        target_request_url: str = mock_requests_get.call_args[0][0]
        self.assertIn("linux-aarch64.tar.gz", target_request_url)

    @patch("platform.system", return_value="Windows")
    @patch("platform.machine", return_value="i386")
    @patch("builtins.print")
    @patch("requests.get")
    def test_windows_x86_resolution(
        self,
        mock_requests_get: MagicMock,
        mock_builtin_print: MagicMock,
        mock_platform_machine: MagicMock,
        mock_platform_system: MagicMock,
    ) -> None:
        mock_network_response: MagicMock = MagicMock(status_code=404)
        mock_network_response.raise_for_status.side_effect = Exception("Mocked abort")
        mock_requests_get.return_value = mock_network_response

        dummy_target_directory: Path = Path("/tmp")
        resolve_and_download_geckodriver(dummy_target_directory)

        target_request_url: str = mock_requests_get.call_args[0][0]
        self.assertIn("win32.zip", target_request_url)


if __name__ == "__main__":
    unittest.main()
