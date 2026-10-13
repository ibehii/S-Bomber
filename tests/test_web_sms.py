"""Tests for IranianWebSMS browser automation components."""

import unittest
from unittest.mock import MagicMock, patch
from lib.WebDepend_Bomb import IranianWebSMS, SELENIUM_AVAILABLE


class TestIranianWebSMS(unittest.TestCase):
    """Verify IranianWebSMS service discovery and mock execution."""

    def test_browser_service_methods_discovery(self) -> None:
        discovered_browser_service_names: list[str] = (
            IranianWebSMS.get_service_methods()
        )
        self.assertEqual(len(discovered_browser_service_names), 13)
        self.assertIn("snapp_app_link", discovered_browser_service_names)
        self.assertIn("snapp_food", discovered_browser_service_names)
        self.assertIn("buskool", discovered_browser_service_names)
        self.assertIn("filimo", discovered_browser_service_names)
        self.assertNotIn("close", discovered_browser_service_names)

    def test_initialization_without_selenium_raises_import_error(self) -> None:
        if not SELENIUM_AVAILABLE:
            with self.assertRaises(ImportError):
                IranianWebSMS("09123456789")

    @patch("lib.WebDepend_Bomb.SELENIUM_AVAILABLE", True)
    @patch("lib.WebDepend_Bomb.webdriver")
    @patch("lib.WebDepend_Bomb.FirefoxService")
    @patch("lib.WebDepend_Bomb.FirefoxOptions")
    def test_mocked_browser_context_manager_and_cleanup(
        self,
        mock_firefox_options_class: MagicMock,
        mock_firefox_service_class: MagicMock,
        mock_webdriver_module: MagicMock,
    ) -> None:
        mock_browser_driver = MagicMock()
        mock_webdriver_module.Firefox.return_value = mock_browser_driver

        web_sender_instance = IranianWebSMS("09123456789")

        with web_sender_instance as active_web_sender:
            self.assertIs(active_web_sender, web_sender_instance)
            self.assertIsNotNone(active_web_sender.driver)

        mock_browser_driver.quit.assert_called_once()
        self.assertIsNone(web_sender_instance.driver)


if __name__ == "__main__":
    unittest.main()
