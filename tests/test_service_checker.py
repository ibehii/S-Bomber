"""Unit tests for non-intrusive service endpoint health and reachability checker."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from lib.service_checker import (
    SERVICE_ENDPOINTS,
    ServiceHealthResult,
    check_all_services,
    check_single_endpoint,
)


class TestServiceChecker(unittest.TestCase):
    """Test suite for endpoint health probes and reachability checks."""

    def test_service_endpoints_coverage(self) -> None:
        """Verify that standard services are mapped in SERVICE_ENDPOINTS."""
        self.assertIn("divar", SERVICE_ENDPOINTS)
        self.assertIn("digikala", SERVICE_ENDPOINTS)
        self.assertIn("tapsi_passenger", SERVICE_ENDPOINTS)
        self.assertIn("snapp_food", SERVICE_ENDPOINTS)
        self.assertGreater(len(SERVICE_ENDPOINTS), 30)

    @patch("requests.head")
    def test_check_single_endpoint_head_success(self, mock_head: MagicMock) -> None:
        """Successful HEAD response marks endpoint as reachable."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        res = check_single_endpoint("divar", "https://api.divar.ir", timeout_seconds=2.0)
        self.assertTrue(res.is_reachable)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.service_name, "divar")

    @patch("requests.get")
    @patch("requests.head")
    def test_check_single_endpoint_head_405_fallback_to_get(
        self,
        mock_head: MagicMock,
        mock_get: MagicMock,
    ) -> None:
        """When HEAD returns 405 Method Not Allowed, fallback to GET."""
        head_response = MagicMock(spec=requests.Response)
        head_response.status_code = 405
        mock_head.return_value = head_response

        get_response = MagicMock(spec=requests.Response)
        get_response.status_code = 200
        mock_get.return_value = get_response

        res = check_single_endpoint("snapp_food", "https://snappfood.ir", timeout_seconds=2.0)
        self.assertTrue(res.is_reachable)
        self.assertEqual(res.status_code, 200)
        mock_get.assert_called_once()

    @patch("requests.head")
    def test_check_single_endpoint_connection_error(self, mock_head: MagicMock) -> None:
        """Network timeout or connection error marks endpoint as unreachable."""
        mock_head.side_effect = requests.ConnectionError("Connection refused")

        res = check_single_endpoint("down_service", "https://down.example.com", timeout_seconds=1.0)
        self.assertFalse(res.is_reachable)
        self.assertIsNone(res.status_code)
        self.assertIn("Connection refused", str(res.error_message))

    @patch("lib.service_checker.check_single_endpoint")
    def test_check_all_services(self, mock_check_single: MagicMock) -> None:
        """Verify check_all_services runs probes concurrently and returns list."""
        mock_check_single.return_value = ServiceHealthResult(
            service_name="mock_svc",
            endpoint_url="https://example.com",
            is_reachable=True,
            status_code=200,
            latency_ms=45.0,
        )

        results = check_all_services(
            selected_services=["divar", "digikala"],
            timeout_seconds=2.0,
        )
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.is_reachable for r in results))


if __name__ == "__main__":
    unittest.main()
