"""Async (webhook-delivered) job receipts and status lookups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import quote

from typing_extensions import Literal, TypedDict

if TYPE_CHECKING:
    from ._base import AsyncBaseClient, BaseClient

AsyncJobStatus = Literal["queued", "running", "complete", "failed", "expired"]
AsyncWebhookStatus = Literal["not_configured", "waiting", "pending", "sending", "delivered", "failed"]


class AsyncWebhookState(TypedDict):
    status: AsyncWebhookStatus
    attempts: int
    response_status: int
    """HTTP status from your webhook's last response, or 0 when unavailable."""


class AsyncJob(TypedDict):
    job_id: str
    status: AsyncJobStatus
    status_url: str
    result_url: str
    accepted_at: str
    result_expires_at: Optional[str]
    """When the stored result expires (one hour after completion), or None before then."""
    result_status: Optional[int]
    """HTTP status of the completed search, or None before completion."""
    error: Optional[str]
    webhook: AsyncWebhookState


class AsyncReceipt(TypedDict):
    """Returned by ``.submit()`` and ``client.async_jobs.status()``."""

    success: Literal[True]
    request_id: str
    """The request ID used in history and in the final response."""
    data: AsyncJob


def _job_path(job_id: str) -> str:
    if not isinstance(job_id, str) or not job_id:
        raise ValueError("job_id must be a non-empty string")
    return f"/v1/async/requests/{quote(job_id, safe='')}"


class AsyncJobsResource:
    """Status and results for jobs started with ``.submit()``.

    Webhooks are the primary way to receive results; use these for troubleshooting,
    no more often than every five seconds.
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def status(self, job_id: str, *, timeout: Optional[float] = None) -> AsyncReceipt:
        """Current status of an async job."""
        return self._client._request("GET", _job_path(job_id), timeout=timeout)

    def result(self, job_id: str, *, timeout: Optional[float] = None) -> Any:
        """The completed response, exactly as the endpoint would have returned it.

        Returns the job receipt while the job is still running. Raises the original
        error if the search failed, and a 410 ``APIStatusError`` once the result expired.
        """
        return self._client._request("GET", f"{_job_path(job_id)}/result", timeout=timeout)


class AsyncAsyncJobsResource:
    """Status and results for jobs started with ``.submit()``, for :class:`AsyncPrismCrawl`."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def status(self, job_id: str, *, timeout: Optional[float] = None) -> AsyncReceipt:
        """Current status of an async job."""
        return await self._client._request("GET", _job_path(job_id), timeout=timeout)

    async def result(self, job_id: str, *, timeout: Optional[float] = None) -> Any:
        """The completed response. See :meth:`AsyncJobsResource.result`."""
        return await self._client._request("GET", f"{_job_path(job_id)}/result", timeout=timeout)
