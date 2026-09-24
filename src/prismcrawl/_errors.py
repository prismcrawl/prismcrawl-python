"""Exceptions raised by the PrismCrawl client."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

import httpx

__all__ = [
    "PrismCrawlError",
    "APIConnectionError",
    "APITimeoutError",
    "APIStatusError",
    "BadRequestError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "NotFoundError",
    "PayloadTooLargeError",
    "RateLimitError",
    "InternalServerError",
]


class PrismCrawlError(Exception):
    """Base class for every error raised by this package."""


class APIConnectionError(PrismCrawlError):
    """The request never produced an HTTP response (DNS, TLS, connection reset, ...)."""

    def __init__(self, message: str = "Connection error.", *, request: Optional[httpx.Request] = None) -> None:
        super().__init__(message)
        self.request = request


class APITimeoutError(APIConnectionError):
    """The request timed out."""

    def __init__(self, *, request: Optional[httpx.Request] = None) -> None:
        super().__init__("Request timed out.", request=request)


class APIStatusError(PrismCrawlError):
    """The API returned a non-2xx response.

    Attributes:
        status_code: HTTP status code.
        code: Machine-readable error code from the response body, such as ``invalid_request``.
        message: Human-readable error message.
        request_id: PrismCrawl request id. Include it when contacting support.
        body: The decoded response body, when it was JSON.
        response: The underlying ``httpx.Response``.
    """

    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response,
        body: Optional[Any],
        code: Optional[str],
        request_id: Optional[str],
    ) -> None:
        super().__init__(message)
        self.message = message
        self.response = response
        self.status_code = response.status_code
        self.body = body
        self.code = code
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [f"{self.status_code}"]
        if self.code:
            parts.append(self.code)
        text = f"[{' '.join(parts)}] {self.message}"
        if self.request_id:
            text += f" (request_id: {self.request_id})"
        return text


class BadRequestError(APIStatusError):
    """400: the request body or pagination token is invalid. No credit is used."""


class AuthenticationError(APIStatusError):
    """401: the API key is missing, invalid, expired, or revoked."""


class InsufficientCreditsError(APIStatusError):
    """402: the account has no search credits left."""


class NotFoundError(APIStatusError):
    """404: the request or archived artifact does not exist for this API key."""


class PayloadTooLargeError(APIStatusError):
    """413: the request body is too large."""


class RateLimitError(APIStatusError):
    """429: a rate limit was hit.

    Attributes:
        rule: The limit that was hit, when the API names one.
        reset_at: ISO-8601 time when the limit resets, when the API provides one.
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        error = _error_object(self.body)
        self.rule: Optional[str] = error.get("rule")
        self.reset_at: Optional[str] = error.get("reset_at")


class InternalServerError(APIStatusError):
    """5xx: PrismCrawl could not complete the request. No credit is used."""


_STATUS_ERRORS: Mapping[int, type] = {
    400: BadRequestError,
    401: AuthenticationError,
    402: InsufficientCreditsError,
    404: NotFoundError,
    413: PayloadTooLargeError,
    429: RateLimitError,
}


def _error_object(body: Any) -> Dict[str, Any]:
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        return body["error"]
    return {}


def make_status_error(response: httpx.Response) -> APIStatusError:
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text or None
    error = _error_object(body)
    message = error.get("message") or response.reason_phrase or "Request failed."
    request_id = response.headers.get("x-request-id")
    if request_id is None and isinstance(body, dict):
        request_id = body.get("request_id")
    cls = _STATUS_ERRORS.get(response.status_code)
    if cls is None:
        cls = InternalServerError if response.status_code >= 500 else APIStatusError
    return cls(message, response=response, body=body, code=error.get("code"), request_id=request_id)
