"""HTTP transport shared by the sync and async clients."""

from __future__ import annotations

import asyncio
import email.utils
import os
import platform
import random
import time
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

import httpx

from ._errors import APIConnectionError, APITimeoutError, PrismCrawlError, make_status_error
from ._version import __version__

DEFAULT_BASE_URL = "https://api.prismcrawl.com"
DEFAULT_TIMEOUT = 120.0
DEFAULT_MAX_RETRIES = 2
API_KEY_ENV = "PRISMCRAWL_API_KEY"
BASE_URL_ENV = "PRISMCRAWL_BASE_URL"

# Don't sleep longer than this for a rate limit; raise RateLimitError instead.
MAX_RETRY_WAIT = 30.0
INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0


def _resolve_api_key(api_key: Optional[str]) -> str:
    key = api_key if api_key is not None else os.environ.get(API_KEY_ENV)
    if not key or not key.strip():
        raise PrismCrawlError(
            f"No API key provided. Pass api_key=... or set the {API_KEY_ENV} environment variable. "
            "Create a key in the PrismCrawl dashboard."
        )
    return key.strip()


def _user_agent() -> str:
    return f"prismcrawl-python/{__version__} python/{platform.python_version()}"


def _retry_after(response: httpx.Response) -> Optional[float]:
    """Seconds to wait before retrying, from Retry-After or the body's reset_at."""
    header = response.headers.get("retry-after")
    if header:
        try:
            return max(0.0, float(header))
        except ValueError:
            try:
                parsed = email.utils.parsedate_to_datetime(header)
            except (TypeError, ValueError):
                parsed = None
            if parsed is not None:
                return max(0.0, parsed.timestamp() - time.time())
    try:
        body = response.json()
        reset_at = body["error"]["reset_at"]
        reset = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
        if reset.tzinfo is None:
            reset = reset.replace(tzinfo=timezone.utc)
        return max(0.0, reset.timestamp() - time.time())
    except (ValueError, KeyError, TypeError, AttributeError):
        return None


def _backoff(attempt: int) -> float:
    delay = min(INITIAL_RETRY_DELAY * (2**attempt), MAX_RETRY_DELAY)
    return delay * (0.75 + random.random() * 0.5)


def _status_retry_delay(response: httpx.Response, attempt: int) -> Optional[float]:
    """Delay before retrying this response, or None if it should not be retried.

    Failed requests don't use credits, so 429 and 5xx are safe to retry for any method.
    """
    status = response.status_code
    if status == 429:
        wait = _retry_after(response)
        if wait is None:
            return _backoff(attempt)
        return wait if wait <= MAX_RETRY_WAIT else None
    if status >= 500:
        return _backoff(attempt)
    return None


def _transport_retry_delay(error: httpx.TransportError, method: str, attempt: int) -> Optional[float]:
    # A connect failure means the request was never sent. Anything later (read timeout,
    # dropped connection) may have completed a billable search, so only GETs retry.
    if isinstance(error, (httpx.ConnectError, httpx.ConnectTimeout)) or method == "GET":
        return _backoff(attempt)
    return None


def _wrap_transport_error(error: httpx.TransportError) -> APIConnectionError:
    request = getattr(error, "_request", None)
    if isinstance(error, httpx.TimeoutException):
        return APITimeoutError(request=request)
    return APIConnectionError(f"Connection error: {error}", request=request)


def _parse(response: httpx.Response, raw_text: bool) -> Any:
    if response.status_code >= 400:
        raise make_status_error(response)
    if raw_text:
        return response.text
    content_type = response.headers.get("content-type", "")
    if "json" in content_type or not content_type:
        return response.json()
    return response.text


class _ClientConfig:
    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: Optional[float],
        max_retries: int,
        default_headers: Optional[Mapping[str, str]],
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self.api_key = _resolve_api_key(api_key)
        self.base_url = (base_url or os.environ.get(BASE_URL_ENV) or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers: Dict[str, str] = {
            "x-api-key": self.api_key,
            "accept": "application/json",
            "user-agent": _user_agent(),
            **(default_headers or {}),
        }

    def build(
        self,
        client: Any,
        method: str,
        path: str,
        json: Optional[Any],
        params: Optional[Mapping[str, str]],
        timeout: Optional[float],
    ) -> httpx.Request:
        return client.build_request(
            method,
            self.base_url + path,
            json=json,
            params=params,
            headers=self.headers,
            timeout=self.timeout if timeout is None else timeout,
        )


class BaseClient:
    """Synchronous transport. Use :class:`prismcrawl.PrismCrawl`."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._config = _ClientConfig(api_key, base_url, timeout, max_retries, default_headers)
        self._owns_http_client = http_client is None
        self._http = http_client or httpx.Client()

    @property
    def base_url(self) -> str:
        return self._config.base_url

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Any] = None,
        params: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
        raw_text: bool = False,
    ) -> Any:
        request = self._config.build(self._http, method, path, json, params, timeout)
        attempt = 0
        while True:
            try:
                response = self._http.send(request)
            except httpx.TransportError as error:
                delay = _transport_retry_delay(error, method, attempt)
                if delay is None or attempt >= self._config.max_retries:
                    raise _wrap_transport_error(error) from error
            else:
                delay = _status_retry_delay(response, attempt)
                if delay is None or attempt >= self._config.max_retries:
                    return _parse(response, raw_text)
                response.close()
            time.sleep(delay)
            attempt += 1

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._owns_http_client:
            self._http.close()

    def __enter__(self) -> BaseClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncBaseClient:
    """Asynchronous transport. Use :class:`prismcrawl.AsyncPrismCrawl`."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._config = _ClientConfig(api_key, base_url, timeout, max_retries, default_headers)
        self._owns_http_client = http_client is None
        self._http = http_client or httpx.AsyncClient()

    @property
    def base_url(self) -> str:
        return self._config.base_url

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Any] = None,
        params: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
        raw_text: bool = False,
    ) -> Any:
        request = self._config.build(self._http, method, path, json, params, timeout)
        attempt = 0
        while True:
            try:
                response = await self._http.send(request)
            except httpx.TransportError as error:
                delay = _transport_retry_delay(error, method, attempt)
                if delay is None or attempt >= self._config.max_retries:
                    raise _wrap_transport_error(error) from error
            else:
                delay = _status_retry_delay(response, attempt)
                if delay is None or attempt >= self._config.max_retries:
                    return _parse(response, raw_text)
                await response.aclose()
            await asyncio.sleep(delay)
            attempt += 1

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._owns_http_client:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncBaseClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()
