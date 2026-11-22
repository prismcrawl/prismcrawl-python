"""Verify async results delivered to your webhook."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Union

from ._errors import PrismCrawlError

__all__ = ["WebhookEvent", "WebhookVerificationError", "verify_webhook"]


class WebhookVerificationError(PrismCrawlError):
    """The webhook signature is missing, malformed, stale, or doesn't match. Respond with a 4xx."""


@dataclass(frozen=True)
class WebhookEvent:
    """A verified async delivery."""

    event_id: str
    """Unique per job. Retries reuse it, so use it to ignore duplicate deliveries."""
    request_id: Optional[str]
    """The request ID of the completed search."""
    result_status: int
    """HTTP status the search returned. ``body`` is that response, including errors."""
    timestamp: int
    """When this delivery was signed, in Unix seconds."""
    body: Any
    """The completed response: parsed JSON, or ``str`` for HTML and other text responses."""


def _header(headers: Mapping[str, Any], name: str) -> Optional[str]:
    getter = getattr(headers, "get", None)
    # Case-insensitive mappings (httpx, Starlette, Werkzeug, Django's request.headers).
    if getter is not None:
        value = getter(name)
        if value is None:
            value = getter(name.title())
        if value is not None:
            return str(value)
    for key, value in headers.items():
        if key.lower() == name:
            return str(value[0] if isinstance(value, (list, tuple)) else value)
    return None


_SIGNATURE = re.compile(r"^\d+$")
_HEX = re.compile(r"^[0-9a-fA-F]{64}$")


def verify_webhook(
    payload: Union[bytes, str],
    headers: Mapping[str, Any],
    secret: str,
    *,
    tolerance: int = 300,
    now: Optional[float] = None,
) -> WebhookEvent:
    """Verify an async result delivered to your webhook and return it.

    Checks the ``Prism-Signature`` HMAC-SHA256 over the timestamp and the raw body in
    constant time, and rejects timestamps more than ``tolerance`` seconds old. Respond
    with any 2xx within 10 seconds to acknowledge the delivery.

    Args:
        payload: The raw request body, exactly as received. Don't parse and re-serialize it.
        headers: The request headers.
        secret: The ``webhook_secret`` you sent with the async request.
        tolerance: Reject signatures older than this many seconds. Defaults to 300.
        now: Current Unix time, for testing. Defaults to ``time.time()``.

    Raises:
        WebhookVerificationError: If the delivery isn't authentic or is stale.
    """
    if not secret:
        raise WebhookVerificationError("secret is required")
    signature = _header(headers, "prism-signature")
    if not signature:
        raise WebhookVerificationError("Missing Prism-Signature header")
    parts = dict(part.strip().split("=", 1) for part in signature.split(",") if "=" in part)
    t, v1 = parts.get("t", ""), parts.get("v1", "")
    if not _SIGNATURE.match(t) or not _HEX.match(v1):
        raise WebhookVerificationError("Malformed Prism-Signature header")
    timestamp = int(t)
    if abs((time.time() if now is None else now) - timestamp) > tolerance:
        raise WebhookVerificationError("Webhook timestamp is outside the allowed tolerance")

    body = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
    expected = hmac.new(secret.encode("utf-8"), f"{t}.".encode("ascii") + body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, v1.lower()):
        raise WebhookVerificationError("Webhook signature doesn't match")

    event_id = _header(headers, "prism-event-id")
    if not event_id:
        raise WebhookVerificationError("Missing Prism-Event-Id header")
    text = body.decode("utf-8")
    parsed: Any = text
    if "json" in (_header(headers, "content-type") or ""):
        try:
            parsed = json.loads(text)
        except ValueError as error:
            raise WebhookVerificationError("Webhook body isn't valid JSON") from error
    return WebhookEvent(
        event_id=event_id,
        request_id=_header(headers, "prism-request-id"),
        result_status=int(_header(headers, "prism-result-status") or 0),
        timestamp=timestamp,
        body=parsed,
    )
