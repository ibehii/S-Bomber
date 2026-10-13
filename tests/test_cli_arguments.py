"""Tests for command-line arguments parsing in Bomber.py."""

import unittest
from Bomber import parse_command_line_arguments


class TestCommandLineArguments(unittest.TestCase):
    """Verify CLI options parsing, flag handling, and defaults."""

    def test_default_cli_arguments_configuration(self) -> None:
        parsed_options = parse_command_line_arguments([])
        self.assertIsNone(parsed_options.phone)
        self.assertEqual(parsed_options.interval, 1.6)
        self.assertEqual(parsed_options.timeout, 10.0)
        self.assertFalse(parsed_options.no_browser)
        self.assertFalse(parsed_options.only_browser)

    def test_custom_phone_and_interval_arguments(self) -> None:
        raw_cli_tokens: list[str] = [
            "--phone",
            "09123456789",
            "--interval",
            "2.5",
        ]
        parsed_options = parse_command_line_arguments(raw_cli_tokens)
        self.assertEqual(parsed_options.phone, "09123456789")
        self.assertEqual(parsed_options.interval, 2.5)

    def test_short_flags_parsing(self) -> None:
        raw_cli_tokens: list[str] = [
            "-p",
            "+989123456789",
            "-i",
            "0.8",
            "-t",
            "5.0",
        ]
        parsed_options = parse_command_line_arguments(raw_cli_tokens)
        self.assertEqual(parsed_options.phone, "+989123456789")
        self.assertEqual(parsed_options.interval, 0.8)
        self.assertEqual(parsed_options.timeout, 5.0)

    def test_no_browser_and_only_browser_flags(self) -> None:
        no_browser_options = parse_command_line_arguments(["--no-browser"])
        self.assertTrue(no_browser_options.no_browser)
        self.assertFalse(no_browser_options.only_browser)

        only_browser_options = parse_command_line_arguments(["--only-browser"])
        self.assertTrue(only_browser_options.only_browser)
        self.assertFalse(only_browser_options.no_browser)


if __name__ == "__main__":
    unittest.main()
