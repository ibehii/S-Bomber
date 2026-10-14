# GitHub: https://github.com/beh185
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Domain exception definitions and error handling decorators for S-Bomber."""

from functools import wraps
from typing import Any, Callable
import requests.exceptions


class BombError(Exception):
    """Base exception class for all S-Bomber related errors."""

    def __init__(self, *exception_arguments: object) -> None:
        super().__init__(*exception_arguments)


class BombServerError(BombError):
    """Raised when a remote SMS provider server returns a 5xx error or fails to respond."""

    def __init__(
        self,
        *exception_arguments: object,
        status_code: int | None = None,
    ) -> None:
        super().__init__(*exception_arguments)
        self.status_code: int | None = status_code

    def __str__(self) -> str:
        if self.args:
            return str(self.args[0])
        return "The remote server failed to respond or encountered an internal error"


class BombClientError(BombError):
    """Raised when the remote SMS provider rejects the request with a 4xx client error."""

    def __init__(
        self,
        *exception_arguments: object,
        status_code: int | None = None,
    ) -> None:
        super().__init__(*exception_arguments)
        self.status_code: int | None = status_code

    def __str__(self) -> str:
        if self.args:
            return str(self.args[0])
        return "The server cannot or will not process the request due to perceived client error"


class BombConnectionError(BombError, ConnectionError):
    """Raised when network connectivity fails, timeouts occur, or DNS resolution fails."""

    def __init__(self, *exception_arguments: object) -> None:
        super().__init__(*exception_arguments)

    def __str__(self) -> str:
        if self.args:
            return str(self.args[0])
        return "Failed to establish a network connection to the remote service"


def error_handler(service_function: Callable[..., Any]) -> Callable[..., bool]:
    """Decorate SMS service provider calls to standardize response evaluation and error handling.

    Parameters
    ----------
    service_function : Callable[..., Any]
        The underlying HTTP service dispatch function to execute.

    Returns
    -------
    Callable[..., bool]
        Wrapped callable returning True upon success, or raising appropriate domain exceptions.
    """
    @wraps(service_function)
    def wrapped_service_executor(
        *service_arguments: Any,
        **service_keyword_arguments: Any,
    ) -> bool:
        try:
            service_response = service_function(
                *service_arguments,
                **service_keyword_arguments,
            )

            # If the underlying function returned an HTTP Response, inspect status code
            if service_response is not None:
                status_code = getattr(service_response, "status_code", None)
                if isinstance(status_code, int):
                    if 400 <= status_code <= 499:
                        raise BombClientError(
                            f"Client error ({status_code}) returned by service",
                            status_code=status_code,
                        )
                    if 500 <= status_code <= 599:
                        raise BombServerError(
                            f"Server error ({status_code}) returned by service",
                            status_code=status_code,
                        )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout,
        ) as request_network_error:
            raise BombConnectionError(
                f"Network connection failed: {request_network_error}"
            ) from request_network_error
        except requests.exceptions.RequestException as general_request_error:
            raise BombServerError(
                f"Request execution failed: {general_request_error}"
            ) from general_request_error

        return True

    return wrapped_service_executor


__all__ = [
    "BombError",
    "BombServerError",
    "BombClientError",
    "BombConnectionError",
    "error_handler",
]
