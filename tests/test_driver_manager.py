"""Unit tests for automated WebDriver resolution (webdriver-manager and fallbacks)."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from lib.driver_manager import (
    resolve_chromedriver_executable,
    resolve_geckodriver_executable,
)


class TestDriverManager(unittest.TestCase):
    """Test suite for ChromeDriver and GeckoDriver binary resolution."""

    def test_custom_path_exists_chromedriver(self) -> None:
        """When an existing custom path is provided, it is resolved and returned."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            result = resolve_chromedriver_executable(tmp_file.name)
            self.assertEqual(result, str(Path(tmp_file.name).resolve()))

    @patch("shutil.which")
    def test_system_path_chromedriver(self, mock_which: MagicMock) -> None:
        """When chromedriver is on PATH, it is returned."""
        mock_which.return_value = "/usr/bin/chromedriver"
        result = resolve_chromedriver_executable(custom_path=None)
        self.assertEqual(result, "/usr/bin/chromedriver")
        mock_which.assert_called_with("chromedriver")

    @patch("shutil.which", return_value=None)
    @patch("lib.driver_manager.WEBDRIVER_MANAGER_AVAILABLE", True)
    @patch("lib.driver_manager.ChromeDriverManager")
    def test_webdriver_manager_chromedriver(
        self,
        mock_manager_class: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """When system PATH fails, webdriver-manager is queried."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            mock_instance = MagicMock()
            mock_instance.install.return_value = tmp_file.name
            mock_manager_class.return_value = mock_instance

            result = resolve_chromedriver_executable(custom_path=None)
            self.assertEqual(result, tmp_file.name)

    @patch("shutil.which", return_value=None)
    @patch("lib.driver_manager.WEBDRIVER_MANAGER_AVAILABLE", False)
    def test_chromedriver_fallback_none(self, mock_which: MagicMock) -> None:
        """When no driver is available, returns None without raising exceptions."""
        result = resolve_chromedriver_executable(custom_path=None)
        self.assertIsNone(result)

    def test_custom_path_exists_geckodriver(self) -> None:
        """When an existing custom path is provided for geckodriver, it is returned."""
        with tempfile.NamedTemporaryFile() as tmp_file:
            result = resolve_geckodriver_executable(tmp_file.name)
            self.assertEqual(result, str(Path(tmp_file.name).resolve()))

    def test_local_binary_geckodriver(self) -> None:
        """When local geckodriver binary exists in workspace, it is used."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_bin = Path(tmp_dir) / "geckodriver"
            local_bin.write_text("dummy binary")
            result = resolve_geckodriver_executable(
                custom_path=None,
                workspace_root=tmp_dir,
            )
            self.assertEqual(result, str(local_bin))

    @patch("shutil.which")
    def test_system_path_geckodriver(self, mock_which: MagicMock) -> None:
        """When geckodriver is on system PATH, it is returned."""
        mock_which.return_value = "/usr/bin/geckodriver"
        with tempfile.TemporaryDirectory() as empty_dir:
            result = resolve_geckodriver_executable(
                custom_path=None,
                workspace_root=empty_dir,
            )
            self.assertEqual(result, "/usr/bin/geckodriver")

    @patch("shutil.which", return_value=None)
    @patch("lib.driver_manager.WEBDRIVER_MANAGER_AVAILABLE", True)
    @patch("lib.driver_manager.GeckoDriverManager")
    def test_webdriver_manager_geckodriver(
        self,
        mock_manager_class: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """When system PATH fails, webdriver-manager geckodriver is queried."""
        with tempfile.TemporaryDirectory() as empty_dir:
            with tempfile.NamedTemporaryFile() as tmp_file:
                mock_instance = MagicMock()
                mock_instance.install.return_value = tmp_file.name
                mock_manager_class.return_value = mock_instance

                result = resolve_geckodriver_executable(
                    custom_path=None,
                    workspace_root=empty_dir,
                )
                self.assertEqual(result, tmp_file.name)


if __name__ == "__main__":
    unittest.main()
