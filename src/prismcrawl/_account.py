"""Request history across every endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, Iterator, Optional
from urllib.parse import quote

from typing_extensions import Literal

from .types import RequestHistoryListResponse

if TYPE_CHECKING:
    from ._base import AsyncBaseClient, BaseClient

_PATH = "/v1/account/requests"


def _query(**params: Any) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        out["from" if key == "from_" else key] = str(value)
    return out


def _request_path(request_id: str) -> str:
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("request_id must be a non-empty string")
    return f"{_PATH}/{quote(request_id, safe='')}"


_LIST_DOC = """Search your request history, newest first.

        Args:
            q: Exact request ID, matched case-insensitively.
            from_: Inclusive lower bound on completion time, as an ISO 8601 timestamp.
            to: Inclusive upper bound on completion time, as an ISO 8601 timestamp.
            provider: Provider or service ID, such as ``google``, ``google_maps``, or
                ``yelp_reviews``.
            status: The original request's outcome.
            format: Recorded response format, or ``zero_trace`` for limited zero-trace
                audit records.
            archive: Whether the saved response archive is available and unexpired.
            limit: Rows per page, 1 to 100. Defaults to 50.
            cursor: ``next_cursor`` from the previous page. Omit for the first page.
            timeout: Override the client timeout for this call, in seconds.
        """

Status = Optional[Literal["success", "failure"]]
Format = Optional[Literal["json", "html+br+base64", "md", "zero_trace"]]
Archive = Optional[Literal["available", "unavailable"]]


class AccountRequestsResource:
    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list(
        self,
        *,
        q: Optional[str] = None,
        from_: Optional[str] = None,
        to: Optional[str] = None,
        provider: Optional[str] = None,
        status: Status = None,
        format: Format = None,
        archive: Archive = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> RequestHistoryListResponse:
        params = _query(
            q=q, from_=from_, to=to, provider=provider, status=status, format=format, archive=archive,
            limit=limit, cursor=cursor,
        )  # fmt: skip
        return self._client._request("GET", _PATH, params=params, timeout=timeout)

    list.__doc__ = _LIST_DOC

    def pages(
        self,
        *,
        q: Optional[str] = None,
        from_: Optional[str] = None,
        to: Optional[str] = None,
        provider: Optional[str] = None,
        status: Status = None,
        format: Format = None,
        archive: Archive = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        timeout: Optional[float] = None,
        max_pages: Optional[int] = None,
    ) -> Iterator[RequestHistoryListResponse]:
        """Iterate over pages of request history, following ``next_cursor``."""
        fetched = 0
        while max_pages is None or fetched < max_pages:
            page = self.list(
                q=q, from_=from_, to=to, provider=provider, status=status, format=format, archive=archive,
                limit=limit, cursor=cursor, timeout=timeout,
            )  # fmt: skip
            fetched += 1
            yield page
            cursor = page["data"].get("next_cursor") or None
            if not cursor:
                return

    def get(self, request_id: str, *, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Metadata for any past request, by request ID."""
        return self._client._request("GET", _request_path(request_id), timeout=timeout)


class AsyncAccountRequestsResource:
    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        q: Optional[str] = None,
        from_: Optional[str] = None,
        to: Optional[str] = None,
        provider: Optional[str] = None,
        status: Status = None,
        format: Format = None,
        archive: Archive = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> RequestHistoryListResponse:
        params = _query(
            q=q, from_=from_, to=to, provider=provider, status=status, format=format, archive=archive,
            limit=limit, cursor=cursor,
        )  # fmt: skip
        return await self._client._request("GET", _PATH, params=params, timeout=timeout)

    list.__doc__ = _LIST_DOC

    async def pages(
        self,
        *,
        q: Optional[str] = None,
        from_: Optional[str] = None,
        to: Optional[str] = None,
        provider: Optional[str] = None,
        status: Status = None,
        format: Format = None,
        archive: Archive = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        timeout: Optional[float] = None,
        max_pages: Optional[int] = None,
    ) -> AsyncIterator[RequestHistoryListResponse]:
        """Iterate over pages of request history, following ``next_cursor``."""
        fetched = 0
        while max_pages is None or fetched < max_pages:
            page = await self.list(
                q=q, from_=from_, to=to, provider=provider, status=status, format=format, archive=archive,
                limit=limit, cursor=cursor, timeout=timeout,
            )  # fmt: skip
            fetched += 1
            yield page
            cursor = page["data"].get("next_cursor") or None
            if not cursor:
                return

    async def get(self, request_id: str, *, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Metadata for any past request, by request ID."""
        return await self._client._request("GET", _request_path(request_id), timeout=timeout)


class AccountResource:
    """Account-level endpoints."""

    def __init__(self, client: BaseClient) -> None:
        self.requests = AccountRequestsResource(client)


class AsyncAccountResource:
    """Account-level endpoints."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self.requests = AsyncAccountRequestsResource(client)
