"""Tests for IranianWebSMS browser automation components."""

import unittest
from unittest.mock import MagicMock, patch
from lib.WebDepend_Bomb import IranianWebSMS, SELENIUM_AVAILABLE


class TestIranianWebSMS(unittest.TestCase):
    """Verify IranianWebSMS service discovery, driver selection, options, and mock execution."""

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

    def test_filter_service_methods(self) -> None:
        filtered = IranianWebSMS.filter_service_methods(["snapp_food", "filimo"])
        self.assertIn("snapp_food", filtered)
        self.assertIn("filimo", filtered)
        self.assertEqual(len(filtered), 2)

        # Empty filter returns all
        all_methods = IranianWebSMS.filter_service_methods([])
        self.assertEqual(len(all_methods), 13)

    def test_initialization_without_selenium_raises_import_error(self) -> None:
        if not SELENIUM_AVAILABLE:
            with self.assertRaises(ImportError):
                IranianWebSMS("09123456789")

    @patch("lib.WebDepend_Bomb.SELENIUM_AVAILABLE", True)
    @patch("lib.WebDepend_Bomb.webdriver")
    @patch("lib.WebDepend_Bomb.ChromeService")
    @patch("lib.WebDepend_Bomb.ChromeOptions")
    def test_chrome_driver_initialization_default(
        self,
        mock_chrome_options_class: MagicMock,
        mock_chrome_service_class: MagicMock,
        mock_webdriver_module: MagicMock,
    ) -> None:
        mock_chrome_driver = MagicMock()
        mock_webdriver_module.Chrome.return_value = mock_chrome_driver

        web_sender_instance = IranianWebSMS("09123456789", browser_type="chrome")

        self.assertEqual(web_sender_instance.browser_type, "chrome")
        mock_webdriver_module.Chrome.assert_called_once()
        mock_chrome_driver.implicitly_wait.assert_called_with(6)

        with web_sender_instance as active_web_sender:
            self.assertIs(active_web_sender, web_sender_instance)
            self.assertIsNotNone(active_web_sender.driver)

        mock_chrome_driver.quit.assert_called_once()
        self.assertIsNone(web_sender_instance.driver)

    @patch("lib.WebDepend_Bomb.SELENIUM_AVAILABLE", True)
    @patch("lib.WebDepend_Bomb.webdriver")
    @patch("lib.WebDepend_Bomb.FirefoxService")
    @patch("lib.WebDepend_Bomb.FirefoxOptions")
    def test_firefox_driver_explicit_selection(
        self,
        mock_firefox_options_class: MagicMock,
        mock_firefox_service_class: MagicMock,
        mock_webdriver_module: MagicMock,
    ) -> None:
        mock_firefox_driver = MagicMock()
        mock_webdriver_module.Firefox.return_value = mock_firefox_driver

        web_sender_instance = IranianWebSMS("09123456789", browser_type="firefox")

        self.assertEqual(web_sender_instance.browser_type, "firefox")
        mock_webdriver_module.Firefox.assert_called_once()
        mock_firefox_driver.implicitly_wait.assert_called_with(6)

        web_sender_instance.close()
        mock_firefox_driver.quit.assert_called_once()

    @patch("lib.WebDepend_Bomb.SELENIUM_AVAILABLE", True)
    @patch("lib.WebDepend_Bomb.webdriver")
    @patch("lib.WebDepend_Bomb.ChromeService")
    @patch("lib.WebDepend_Bomb.ChromeOptions")
    @patch("lib.WebDepend_Bomb.FirefoxService")
    @patch("lib.WebDepend_Bomb.FirefoxOptions")
    def test_chrome_fallback_to_firefox_on_chrome_failure(
        self,
        mock_firefox_options_class: MagicMock,
        mock_firefox_service_class: MagicMock,
        mock_chrome_options_class: MagicMock,
        mock_chrome_service_class: MagicMock,
        mock_webdriver_module: MagicMock,
    ) -> None:
        mock_webdriver_module.Chrome.side_effect = Exception("ChromeDriver binary missing")
        mock_firefox_driver = MagicMock()
        mock_webdriver_module.Firefox.return_value = mock_firefox_driver

        web_sender_instance = IranianWebSMS("09123456789", browser_type="chrome")

        self.assertEqual(web_sender_instance.browser_type, "firefox")
        mock_webdriver_module.Chrome.assert_called_once()
        mock_webdriver_module.Firefox.assert_called_once()

        web_sender_instance.close()
        mock_firefox_driver.quit.assert_called_once()

    @patch("lib.WebDepend_Bomb.SELENIUM_AVAILABLE", True)
    @patch("lib.WebDepend_Bomb.webdriver")
    @patch("lib.WebDepend_Bomb.ChromeService")
    @patch("lib.WebDepend_Bomb.ChromeOptions")
    @patch("lib.WebDepend_Bomb.FirefoxService")
    @patch("lib.WebDepend_Bomb.FirefoxOptions")
    def test_both_drivers_fail_raises_original_chrome_error(
        self,
        mock_firefox_options_class: MagicMock,
        mock_firefox_service_class: MagicMock,
        mock_chrome_options_class: MagicMock,
        mock_chrome_service_class: MagicMock,
        mock_webdriver_module: MagicMock,
    ) -> None:
        mock_webdriver_module.Chrome.side_effect = RuntimeError("Chrome failed")
        mock_webdriver_module.Firefox.side_effect = RuntimeError("Firefox failed")

        with self.assertRaises(RuntimeError) as context:
            IranianWebSMS("09123456789", browser_type="chrome")
        self.assertIn("Chrome failed", str(context.exception))


if __name__ == "__main__":
    unittest.main()
