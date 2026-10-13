"""Tests for S-Bomber exception hierarchy and the error_handler decorator."""

from typing import Any
import unittest
from unittest.mock import MagicMock
import requests.exceptions

from lib.bomb_exceptions import (
    BombClientError,
    BombConnectionError,
    BombError,
    BombServerError,
    error_handler,
)


class TestBombExceptionsHierarchy(unittest.TestCase):
    """Verify exception inheritance and string representations."""

    def test_bomb_error_is_base_exception(self) -> None:
        custom_error_instance: BombError = BombError("Custom message")
        self.assertIsInstance(custom_error_instance, Exception)
        self.assertEqual(str(custom_error_instance), "Custom message")

    def test_bomb_client_error_subclasses_bomb_error(self) -> None:
        client_error_instance: BombClientError = BombClientError()
        self.assertIsInstance(client_error_instance, BombError)
        self.assertIn("client error", str(client_error_instance).lower())

        custom_client_error: BombClientError = BombClientError("Unauthorized access")
        self.assertEqual(str(custom_client_error), "Unauthorized access")

    def test_bomb_server_error_subclasses_bomb_error(self) -> None:
        server_error_instance: BombServerError = BombServerError()
        self.assertIsInstance(server_error_instance, BombError)
        self.assertIn("server", str(server_error_instance).lower())

        custom_server_error: BombServerError = BombServerError("Internal Gateway Failure")
        self.assertEqual(str(custom_server_error), "Internal Gateway Failure")

    def test_bomb_connection_error_subclasses_connection_error_and_bomb_error(self) -> None:
        """Crucial test: callers catching built-in ConnectionError must catch BombConnectionError."""
        network_error_instance: BombConnectionError = BombConnectionError()
        self.assertIsInstance(network_error_instance, BombError)
        self.assertIsInstance(network_error_instance, ConnectionError)


class TestErrorHandlerDecorator(unittest.TestCase):
    """Verify behavior of error_handler across various HTTP status codes and exceptions."""

    def test_successful_http_response_returns_true(self) -> None:
        mock_response_object = MagicMock(status_code=200)

        @error_handler
        def dummy_successful_service() -> Any:
            return mock_response_object

        execution_result: bool = dummy_successful_service()
        self.assertTrue(execution_result)

    def test_client_error_status_code_raises_bomb_client_error(self) -> None:
        client_status_codes: list[int] = [400, 401, 403, 404, 422, 429]

        for target_status_code in client_status_codes:
            mock_client_failure_response = MagicMock(status_code=target_status_code)

            @error_handler
            def dummy_client_error_service() -> Any:
                return mock_client_failure_response

            with self.assertRaises(BombClientError) as caught_client_error_context:
                dummy_client_error_service()
            self.assertEqual(caught_client_error_context.exception.status_code, target_status_code)

    def test_server_error_status_code_raises_bomb_server_error(self) -> None:
        server_status_codes: list[int] = [500, 502, 503, 504]

        for target_status_code in server_status_codes:
            mock_server_failure_response = MagicMock(status_code=target_status_code)

            @error_handler
            def dummy_server_error_service() -> Any:
                return mock_server_failure_response

            with self.assertRaises(BombServerError) as caught_server_error_context:
                dummy_server_error_service()
            self.assertEqual(caught_server_error_context.exception.status_code, target_status_code)

    def test_requests_connection_error_raises_bomb_connection_error(self) -> None:
        @error_handler
        def dummy_disconnected_service() -> Any:
            raise requests.exceptions.ConnectionError("DNS lookup failed")

        with self.assertRaises(ConnectionError):
            dummy_disconnected_service()

    def test_requests_timeout_error_raises_bomb_connection_error(self) -> None:
        @error_handler
        def dummy_timeout_service() -> Any:
            raise requests.exceptions.Timeout("Socket read timed out")

        with self.assertRaises(ConnectionError):
            dummy_timeout_service()

    def test_function_returning_none_defaults_to_true(self) -> None:
        @error_handler
        def dummy_legacy_service_returning_none() -> Any:
            return None

        execution_result: bool = dummy_legacy_service_returning_none()
        self.assertTrue(execution_result)


if __name__ == "__main__":
    unittest.main()
