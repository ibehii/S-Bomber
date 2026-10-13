"""Security audit tests verifying headers sanitation, credential scrubbing, and safety."""

import re
import unittest
from unittest.mock import MagicMock
from lib import Headers
from lib.Bomb import IranianSMS


class TestHeadersSecurityAndSanitization(unittest.TestCase):
    """Ensure no secrets, tokens, PII, GPS coordinates, or Content-Length headers exist."""

    def test_no_content_length_headers_in_any_service(self) -> None:
        """Content-Length headers must be omitted so requests/urllib3 calculates them dynamically."""
        for exported_header_name in Headers.__all__:
            header_dictionary = getattr(Headers, exported_header_name)
            self.assertIsInstance(header_dictionary, dict)
            for header_key in header_dictionary.keys():
                self.assertNotEqual(
                    header_key.lower(),
                    "content-length",
                    f"Found hardcoded Content-Length in {exported_header_name}",
                )

    def test_no_hardcoded_cookies_in_any_service(self) -> None:
        """Personal tracking cookies and expired session cookies must not be baked into headers."""
        for exported_header_name in Headers.__all__:
            header_dictionary = getattr(Headers, exported_header_name)
            for header_key in header_dictionary.keys():
                self.assertNotIn(
                    "cookie",
                    header_key.lower(),
                    f"Found hardcoded Cookie in {exported_header_name}",
                )

    def test_no_pii_phone_numbers_in_headers(self) -> None:
        """Verify that previously leaked author phone numbers do not appear in any header values."""
        phone_patterns = ["09385347412", "9385347412"]
        for exported_header_name in Headers.__all__:
            header_dictionary = getattr(Headers, exported_header_name)
            for header_key, header_value in header_dictionary.items():
                for banned_phone in phone_patterns:
                    self.assertNotIn(
                        banned_phone,
                        str(header_value),
                        f"Found leaked phone number {banned_phone} in {exported_header_name} key {header_key}",
                    )

    def test_no_gps_coordinates_in_headers(self) -> None:
        """Verify that user latitude and longitude are not leaked."""
        for exported_header_name in Headers.__all__:
            header_dictionary = getattr(Headers, exported_header_name)
            for header_key, header_value in header_dictionary.items():
                self.assertNotIn(
                    "user_lat",
                    str(header_value),
                    f"Found user_lat coordinate in {exported_header_name}",
                )
                self.assertNotIn(
                    "user_lng",
                    str(header_value),
                    f"Found user_lng coordinate in {exported_header_name}",
                )

    def test_no_hardcoded_auth_or_login_tokens_in_headers(self) -> None:
        """Verify that third-party tokens (Chatwoot, crisp, x-login-token) are removed."""
        forbidden_header_keys = {
            "x-login-token",
            "user-token",
            "x-csrf-token",
        }
        for exported_header_name in Headers.__all__:
            header_dictionary = getattr(Headers, exported_header_name)
            for header_key in header_dictionary.keys():
                self.assertNotIn(
                    header_key.lower(),
                    forbidden_header_keys,
                    f"Found forbidden token header {header_key} in {exported_header_name}",
                )


class TestTapsiDynamicSessionId(unittest.TestCase):
    """Ensure dynamic generation of session identifiers in Tapsi passenger service."""

    def test_tapsi_passenger_generates_unique_dynamic_session_ids(self) -> None:
        mock_http_session: MagicMock = MagicMock()
        mock_successful_response: MagicMock = MagicMock(status_code=200)
        mock_http_session.post.return_value = mock_successful_response

        sms_dispatcher = IranianSMS(
            phone_number="09123456789",
            http_session=mock_http_session,
        )

        sms_dispatcher.tapsi_passenger()
        first_post_call = mock_http_session.post.call_args[1]
        first_session_id = first_post_call["json"]["session_id"]

        sms_dispatcher.tapsi_passenger()
        second_post_call = mock_http_session.post.call_args[1]
        second_session_id = second_post_call["json"]["session_id"]

        self.assertNotEqual(first_session_id, second_session_id)
        # Check UUID format (two UUID4s separated by '--')
        uuid_regex = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        self.assertRegex(first_session_id, uuid_regex)
        self.assertRegex(second_session_id, uuid_regex)


if __name__ == "__main__":
    unittest.main()
