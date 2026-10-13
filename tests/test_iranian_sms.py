"""Tests for IranianSMS provider dispatching and service method integrity."""

import unittest
from unittest.mock import MagicMock
from lib.Bomb import IranianSMS


class TestIranianSMS(unittest.TestCase):
    """Verify IranianSMS initialization, service discovery, and mocked execution."""

    def setUp(self) -> None:
        self.sample_target_phone: str = "09123456789"
        self.mock_http_session: MagicMock = MagicMock()
        self.sms_sender_instance: IranianSMS = IranianSMS(
            phone_number=self.sample_target_phone,
            http_session=self.mock_http_session,
        )

    def test_phone_number_attributes_and_property_formatting(self) -> None:
        self.assertEqual(
            self.sms_sender_instance.phone_number, self.sample_target_phone
        )
        self.assertEqual(
            self.sms_sender_instance.PhoneNumber, self.sample_target_phone
        )
        self.assertEqual(
            self.sms_sender_instance.phone_without_leading_zero, "9123456789"
        )

    def test_phone_without_leading_zero_handles_international_formats(self) -> None:
        international_sender_instance: IranianSMS = IranianSMS(
            phone_number="989123456789",
            http_session=self.mock_http_session,
        )
        self.assertEqual(
            international_sender_instance.phone_without_leading_zero, "9123456789"
        )

    def test_service_methods_discovery_returns_expected_providers_count(self) -> None:
        discovered_service_names: list[str] = (
            IranianSMS.get_service_methods()
        )
        self.assertEqual(len(discovered_service_names), 31)
        self.assertIn("divar", discovered_service_names)
        self.assertIn("tapsi_passenger", discovered_service_names)
        self.assertIn("digikala", discovered_service_names)
        self.assertIn("telewebion", discovered_service_names)
        self.assertNotIn("close", discovered_service_names)
        self.assertNotIn("_post", discovered_service_names)

    def test_all_service_methods_execute_successfully_with_mocked_http_responses(
        self,
    ) -> None:
        """Execute each of the 31 services against a mocked session returning HTTP 200."""
        mock_successful_response: MagicMock = MagicMock(status_code=200)
        self.mock_http_session.post.return_value = mock_successful_response
        self.mock_http_session.get.return_value = mock_successful_response

        for service_provider_name in IranianSMS.get_service_methods():
            service_callable = getattr(
                self.sms_sender_instance, service_provider_name
            )
            dispatch_result: bool = service_callable()
            self.assertTrue(
                dispatch_result,
                f"Service {service_provider_name} failed to return True on success",
            )

    def test_context_manager_lifecycle(self) -> None:
        mock_standalone_session: MagicMock = MagicMock()
        sms_instance_with_owned_session: IranianSMS = IranianSMS(
            phone_number=self.sample_target_phone,
            http_session=mock_standalone_session,
        )
        sms_instance_with_owned_session._owns_session = True

        with sms_instance_with_owned_session as entered_sms_sender:
            self.assertIs(entered_sms_sender, sms_instance_with_owned_session)

        mock_standalone_session.close.assert_called_once()

    def test_default_request_timeout_injected_into_network_calls(self) -> None:
        mock_successful_response: MagicMock = MagicMock(status_code=200)
        self.mock_http_session.post.return_value = mock_successful_response

        self.sms_sender_instance.divar()

        keyword_call_arguments = self.mock_http_session.post.call_args[1]
        self.assertIn("timeout", keyword_call_arguments)
        self.assertEqual(
            keyword_call_arguments["timeout"],
            self.sms_sender_instance.request_timeout,
        )


if __name__ == "__main__":
    unittest.main()
