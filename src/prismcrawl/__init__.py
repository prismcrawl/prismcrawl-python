"""Python client for the PrismCrawl API."""

from . import types
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

__all__ = [
    "PrismCrawl",
    "AsyncPrismCrawl",
    "decode_html",
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
