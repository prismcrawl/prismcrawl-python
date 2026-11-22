"""Base classes for generated endpoints."""

from __future__ import annotations

import uuid
from typing import Any, AsyncIterator, ClassVar, Dict, Iterator, Mapping, Optional, Union, overload
from urllib.parse import quote

from typing_extensions import Literal

from ._base import AsyncBaseClient, BaseClient

Artifact = Literal["json", "html"]


def _build_body(body: Mapping[str, Any], extra_body: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    out = {key: value for key, value in body.items() if value is not None}
    if extra_body:
        out.update(extra_body)
    return out


def _history_params(artifact: Optional[str]) -> Optional[Dict[str, str]]:
    if artifact is None:
        return None
    if artifact not in ("json", "html"):
        raise ValueError('artifact must be "json", "html", or None')
    return {"artifact": artifact}


def _submit_headers(idempotency_key: Optional[str]) -> Dict[str, str]:
    # The key lets PrismCrawl recognize a resent submission and return the existing job.
    return {"prefer": "respond-async", "idempotency-key": idempotency_key or str(uuid.uuid4())}


def _next_body(kind: Optional[str], body: Dict[str, Any], page: Any) -> Optional[Dict[str, Any]]:
    """Request body for the page after `page`, or None when there are no more pages."""
    data = page.get("data") if isinstance(page, dict) else None
    content = data.get("content") if isinstance(data, dict) else None
    if not isinstance(content, dict) or not content.get("has_next_page"):
        return None
    if kind == "token":
        token = content.get("next_page_token")
        return {**body, "next_page_token": token} if token else None
    if kind == "page":
        return {**body, "page": int(body.get("page") or 1) + 1}
    return None


class SyncEndpoint:
    _path: ClassVar[str]
    _pagination: ClassVar[Optional[str]] = None

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def _create(
        self, body: Mapping[str, Any], extra_body: Optional[Mapping[str, Any]], timeout: Optional[float]
    ) -> Any:
        return self._client._request("POST", self._path, json=_build_body(body, extra_body), timeout=timeout)

    def _submit(
        self,
        body: Mapping[str, Any],
        extra_body: Optional[Mapping[str, Any]],
        timeout: Optional[float],
        idempotency_key: Optional[str],
    ) -> Any:
        return self._client._request(
            "POST",
            self._path,
            json=_build_body(body, extra_body),
            timeout=timeout,
            headers=_submit_headers(idempotency_key),
            idempotent=True,
        )

    def _pages(
        self,
        body: Mapping[str, Any],
        extra_body: Optional[Mapping[str, Any]],
        timeout: Optional[float],
        max_pages: Optional[int],
    ) -> Iterator[Any]:
        request: Optional[Dict[str, Any]] = _build_body(body, extra_body)
        fetched = 0
        while request is not None and (max_pages is None or fetched < max_pages):
            page = self._client._request("POST", self._path, json=request, timeout=timeout)
            fetched += 1
            yield page
            request = _next_body(self._pagination, request, page)

    @overload
    def get(self, request_id: str, *, artifact: Literal["html"], timeout: Optional[float] = None) -> str: ...
    @overload
    def get(
        self, request_id: str, *, artifact: Optional[Literal["json"]] = None, timeout: Optional[float] = None
    ) -> Dict[str, Any]: ...
    def get(
        self, request_id: str, *, artifact: Optional[Artifact] = None, timeout: Optional[float] = None
    ) -> Union[str, Dict[str, Any]]:
        """Retrieve a previous request by id.

        Args:
            request_id: The ``request_id`` from an earlier response.
            artifact: ``None`` for request metadata, ``"json"`` for the archived parsed
                response, or ``"html"`` for the archived source HTML (returned as ``str``).
                Requests made with ``zero_trace=True`` have no artifacts.
            timeout: Override the client timeout for this call, in seconds.
        """
        return self._client._request(
            "GET",
            f"{self._path}/{quote(request_id, safe='')}",
            params=_history_params(artifact),
            timeout=timeout,
            raw_text=artifact == "html",
        )


class AsyncEndpoint:
    _path: ClassVar[str]
    _pagination: ClassVar[Optional[str]] = None

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def _create(
        self, body: Mapping[str, Any], extra_body: Optional[Mapping[str, Any]], timeout: Optional[float]
    ) -> Any:
        return await self._client._request("POST", self._path, json=_build_body(body, extra_body), timeout=timeout)

    async def _submit(
        self,
        body: Mapping[str, Any],
        extra_body: Optional[Mapping[str, Any]],
        timeout: Optional[float],
        idempotency_key: Optional[str],
    ) -> Any:
        return await self._client._request(
            "POST",
            self._path,
            json=_build_body(body, extra_body),
            timeout=timeout,
            headers=_submit_headers(idempotency_key),
            idempotent=True,
        )

    async def _pages(
        self,
        body: Mapping[str, Any],
        extra_body: Optional[Mapping[str, Any]],
        timeout: Optional[float],
        max_pages: Optional[int],
    ) -> AsyncIterator[Any]:
        request: Optional[Dict[str, Any]] = _build_body(body, extra_body)
        fetched = 0
        while request is not None and (max_pages is None or fetched < max_pages):
            page = await self._client._request("POST", self._path, json=request, timeout=timeout)
            fetched += 1
            yield page
            request = _next_body(self._pagination, request, page)

    @overload
    async def get(self, request_id: str, *, artifact: Literal["html"], timeout: Optional[float] = None) -> str: ...
    @overload
    async def get(
        self, request_id: str, *, artifact: Optional[Literal["json"]] = None, timeout: Optional[float] = None
    ) -> Dict[str, Any]: ...
    async def get(
        self, request_id: str, *, artifact: Optional[Artifact] = None, timeout: Optional[float] = None
    ) -> Union[str, Dict[str, Any]]:
        """Retrieve a previous request by id.

        Args:
            request_id: The ``request_id`` from an earlier response.
            artifact: ``None`` for request metadata, ``"json"`` for the archived parsed
                response, or ``"html"`` for the archived source HTML (returned as ``str``).
                Requests made with ``zero_trace=True`` have no artifacts.
            timeout: Override the client timeout for this call, in seconds.
        """
        return await self._client._request(
            "GET",
            f"{self._path}/{quote(request_id, safe='')}",
            params=_history_params(artifact),
            timeout=timeout,
            raw_text=artifact == "html",
        )
