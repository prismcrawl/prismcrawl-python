"""The PrismCrawl API clients."""

from __future__ import annotations

from typing import Mapping, Optional

import httpx

from ._account import AccountResource, AsyncAccountResource
from ._async import AsyncAsyncJobsResource, AsyncJobsResource
from ._base import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, AsyncBaseClient, BaseClient
from ._resources import AsyncResources, Resources

__all__ = ["PrismCrawl", "AsyncPrismCrawl"]


class PrismCrawl(BaseClient, Resources):
    """Synchronous PrismCrawl client.

    Example:
        >>> from prismcrawl import PrismCrawl
        >>> client = PrismCrawl(api_key="pc_...")  # or set PRISMCRAWL_API_KEY
        >>> results = client.google.search(query="best espresso machines")

    Args:
        api_key: Your PrismCrawl API key. Defaults to the ``PRISMCRAWL_API_KEY``
            environment variable.
        base_url: API base URL. Defaults to ``PRISMCRAWL_BASE_URL`` or
            ``https://api.prismcrawl.com``.
        timeout: Request timeout in seconds, or ``None`` for no timeout.
        max_retries: Retries for connection failures, rate limits, and server errors.
        default_headers: Extra headers sent with every request.
        http_client: A preconfigured ``httpx.Client`` (proxies, transports, ...). The
            caller is responsible for closing it.
    """

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
        super().__init__(
            api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            http_client=http_client,
        )
        self._init_resources(self)
        self.account = AccountResource(self)
        """Request history across every endpoint."""
        self.async_jobs = AsyncJobsResource(self)
        """Status and results for jobs started with ``.submit()``."""

    def __enter__(self) -> PrismCrawl:
        return self


class AsyncPrismCrawl(AsyncBaseClient, AsyncResources):
    """Asynchronous PrismCrawl client.

    Example:
        >>> from prismcrawl import AsyncPrismCrawl
        >>> async with AsyncPrismCrawl() as client:
        ...     results = await client.google.search(query="best espresso machines")

    Takes the same arguments as :class:`PrismCrawl`, with an ``httpx.AsyncClient``
    for ``http_client``.
    """

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
        super().__init__(
            api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            http_client=http_client,
        )
        self._init_resources(self)
        self.account = AsyncAccountResource(self)
        """Request history across every endpoint."""
        self.async_jobs = AsyncAsyncJobsResource(self)
        """Status and results for jobs started with ``.submit()``."""

    async def __aenter__(self) -> AsyncPrismCrawl:
        return self
