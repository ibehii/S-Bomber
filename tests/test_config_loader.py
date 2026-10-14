"""Unit tests for config_loader module."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lib.config_loader import (
    DEFAULT_CONFIGURATION,
    get_default_config_path,
    load_configuration,
)


class TestConfigLoader(unittest.TestCase):
    """Test loading, parsing, and merging of TOML configuration."""

    def test_default_config_structure(self) -> None:
        """Verify default configuration schema."""
        self.assertIn("general", DEFAULT_CONFIGURATION)
        self.assertIn("bomber", DEFAULT_CONFIGURATION)
        self.assertEqual(DEFAULT_CONFIGURATION["bomber"]["default_driver"], "chrome")
        self.assertTrue(DEFAULT_CONFIGURATION["bomber"]["use_browser"])
        self.assertEqual(DEFAULT_CONFIGURATION["bomber"]["request_interval"], 1.6)
        self.assertFalse(DEFAULT_CONFIGURATION["bomber"]["export_report"])
        self.assertEqual(DEFAULT_CONFIGURATION["bomber"]["export_format"], "json")
        self.assertEqual(DEFAULT_CONFIGURATION["bomber"]["reports_dir"], "reports")
        self.assertEqual(DEFAULT_CONFIGURATION["bomber"]["rounds"], 1)
        self.assertEqual(DEFAULT_CONFIGURATION["bomber"]["round_interval"], 5.0)

    def test_get_default_config_path_returns_path(self) -> None:
        """Default config path should point to config.toml in project root."""
        config_path = get_default_config_path()
        self.assertIsInstance(config_path, Path)
        self.assertTrue(str(config_path).endswith("config.toml"))

    def test_load_non_existent_file_returns_defaults(self) -> None:
        """Non-existent config file returns default configuration without error."""
        non_existent = Path("/non/existent/path/config.toml")
        config = load_configuration(non_existent)
        self.assertEqual(config["bomber"]["default_driver"], "chrome")
        self.assertEqual(config["general"]["telegram"], "https://t.me/dr_xz")

    def test_load_valid_custom_toml(self) -> None:
        """Loading a valid custom TOML file overrides specified values."""
        custom_toml_content = b"""
[general]
telegram = "https://t.me/custom_test"

[bomber]
default_driver = "firefox"
request_interval = 3.5
is_headless = false
selected_services = ["divar", "snapp_food"]
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp_file:
            tmp_file.write(custom_toml_content)
            tmp_path = Path(tmp_file.name)

        try:
            config = load_configuration(tmp_path)
            self.assertEqual(config["general"]["telegram"], "https://t.me/custom_test")
            self.assertEqual(config["general"]["github"], DEFAULT_CONFIGURATION["general"]["github"])
            self.assertEqual(config["bomber"]["default_driver"], "firefox")
            self.assertEqual(config["bomber"]["request_interval"], 3.5)
            self.assertFalse(config["bomber"]["is_headless"])
            self.assertEqual(config["bomber"]["selected_services"], ["divar", "snapp_food"])
            # Unspecified keys retain defaults
            self.assertEqual(config["bomber"]["request_timeout"], 10.0)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_load_malformed_toml_falls_back_to_defaults(self) -> None:
        """Malformed TOML syntax falls back gracefully to defaults."""
        malformed_content = b"[[INVALID TOML CONTENT {{{ not valid"
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp_file:
            tmp_file.write(malformed_content)
            tmp_path = Path(tmp_file.name)

        try:
            config = load_configuration(tmp_path)
            self.assertEqual(config["bomber"]["default_driver"], "chrome")
            self.assertEqual(config["general"]["telegram"], "https://t.me/dr_xz")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_load_partial_toml_sections(self) -> None:
        """TOML with only [bomber] preserves [general] defaults."""
        partial_content = b"""
[bomber]
request_timeout = 25.0
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp_file:
            tmp_file.write(partial_content)
            tmp_path = Path(tmp_file.name)

        try:
            config = load_configuration(tmp_path)
            self.assertEqual(config["bomber"]["request_timeout"], 25.0)
            self.assertEqual(config["bomber"]["default_driver"], "chrome")
            self.assertEqual(config["general"]["telegram"], "https://t.me/dr_xz")
        finally:
            tmp_path.unlink(missing_ok=True)

    @patch("lib.config_loader.tomllib", None)
    def test_load_when_tomllib_is_none(self) -> None:
        """When tomllib is unavailable, defaults are returned cleanly."""
        config = load_configuration()
        self.assertEqual(config["bomber"]["default_driver"], "chrome")


if __name__ == "__main__":
    unittest.main()
