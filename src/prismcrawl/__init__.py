"""Python client for the PrismCrawl API."""

from . import types
from ._async import AsyncReceipt
from ._base import DEFAULT_BASE_URL
from ._client import AsyncPrismCrawl, PrismCrawl
from ._errors import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InsufficientCreditsError,
    InternalServerError,
    NotFoundError,
    PayloadTooLargeError,
    PrismCrawlError,
    RateLimitError,
)
from ._html import decode_html
from ._version import __version__
from ._webhooks import WebhookEvent, WebhookVerificationError, verify_webhook

__all__ = [
    "PrismCrawl",
    "AsyncPrismCrawl",
    "decode_html",
    "verify_webhook",
    "WebhookEvent",
    "WebhookVerificationError",
    "AsyncReceipt",
    "types",
    "DEFAULT_BASE_URL",
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
    "__version__",
]
