from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import inspect
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional

import brotli
import httpx
import pytest

import prismcrawl
from prismcrawl import AsyncPrismCrawl, PrismCrawl, decode_html
from prismcrawl._endpoint import AsyncEndpoint, SyncEndpoint

SPEC = json.loads((Path(__file__).resolve().parent.parent / "openapi.json").read_text())
REQUEST_ID = "66ca8deb-1dc2-4017-865f-c4fb0e3c7c0d"

Handler = Callable[[httpx.Request], httpx.Response]


def ok(content: Optional[Dict[str, Any]] = None) -> httpx.Response:
    return httpx.Response(
        200,
        json={"success": True, "request_id": REQUEST_ID, "data": {"format": "json", "content": content or {}}},
        headers={"x-request-id": REQUEST_ID},
    )


def error(status: int, code: str, message: str, **extra: Any) -> httpx.Response:
    return httpx.Response(
        status,
        json={
            "success": False,
            "request_id": REQUEST_ID,
            "data": None,
            "error": {"code": code, "message": message, **extra},
        },
        headers={"x-request-id": REQUEST_ID},
    )


class Recorder:
    def __init__(self, *responses: Any) -> None:
        self.responses: List[Any] = list(responses)
        self.requests: List[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        response = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(response, Exception):
            raise response
        return response

    def body(self, index: int = -1) -> Dict[str, Any]:
        return json.loads(self.requests[index].content)


def make_client(handler: Handler, **kwargs: Any) -> PrismCrawl:
    return PrismCrawl(api_key="test-key", http_client=httpx.Client(transport=httpx.MockTransport(handler)), **kwargs)


def make_async_client(handler: Handler, **kwargs: Any) -> AsyncPrismCrawl:
    return AsyncPrismCrawl(
        api_key="test-key", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)), **kwargs
    )


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr("prismcrawl._base.time.sleep", lambda _: None)

    async def instant(_: float) -> None:
        return None

    monkeypatch.setattr("prismcrawl._base.asyncio.sleep", instant)
    yield


def test_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRISMCRAWL_API_KEY", "env-key")
    recorder = Recorder(ok())
    client = PrismCrawl(http_client=httpx.Client(transport=httpx.MockTransport(recorder)))
    client.google.search(query="q")
    assert recorder.requests[0].headers["x-api-key"] == "env-key"


def test_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PRISMCRAWL_API_KEY", raising=False)
    with pytest.raises(prismcrawl.PrismCrawlError, match="PRISMCRAWL_API_KEY"):
        PrismCrawl()


def test_base_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRISMCRAWL_BASE_URL", "https://staging.example.com/")
    recorder = Recorder(ok())
    make_client(recorder).google.search(query="q")
    assert str(recorder.requests[0].url) == "https://staging.example.com/v1/google/search"


def test_request_shape() -> None:
    recorder = Recorder(ok({"results": []}))
    client = make_client(recorder, default_headers={"x-extra": "1"})
    response = client.google.maps.search(
        query="coffee shop",
        coordinates={"latitude": 30.2672, "longitude": -97.7431},
        extra_body={"future_param": True},
    )
    request = recorder.requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.prismcrawl.com/v1/google/maps/search"
    assert request.headers["x-api-key"] == "test-key"
    assert request.headers["x-extra"] == "1"
    assert request.headers["user-agent"].startswith(f"prismcrawl-python/{prismcrawl.__version__}")
    # Unset parameters are omitted rather than sent as null.
    assert recorder.body() == {
        "query": "coffee shop",
        "coordinates": {"latitude": 30.2672, "longitude": -97.7431},
        "future_param": True,
    }
    assert response["request_id"] == REQUEST_ID


def test_false_values_are_sent() -> None:
    recorder = Recorder(ok())
    make_client(recorder).google.search(query="q", html=False, start=0)
    assert recorder.body() == {"query": "q", "html": False, "start": 0}


def test_bing_alias() -> None:
    recorder = Recorder(ok())
    client = make_client(recorder)
    assert client.bing is client.microsoft
    client.bing.search(query="q")
    assert recorder.requests[0].url.path == "/v1/microsoft/search"


def test_history_metadata_and_artifacts() -> None:
    recorder = Recorder(
        httpx.Response(200, json={"success": True, "request_id": REQUEST_ID, "data": {"status": "done"}}),
    )
    client = make_client(recorder)
    metadata = client.yelp.reviews.get(REQUEST_ID)
    assert metadata["data"] == {"status": "done"}
    assert recorder.requests[0].method == "GET"
    assert recorder.requests[0].url.path == f"/v1/yelp/reviews/{REQUEST_ID}"
    assert "artifact" not in recorder.requests[0].url.params

    client.yelp.reviews.get(REQUEST_ID, artifact="json")
    assert recorder.requests[1].url.params["artifact"] == "json"


def test_history_html_artifact_returns_text() -> None:
    recorder = Recorder(
        httpx.Response(200, text="<html>hi</html>", headers={"content-type": "text/html; charset=utf-8"})
    )
    html = make_client(recorder).google.search.get(REQUEST_ID, artifact="html")
    assert html == "<html>hi</html>"
    assert recorder.requests[0].url.params["artifact"] == "html"


def test_history_escapes_request_id() -> None:
    recorder = Recorder(ok())
    make_client(recorder).google.search.get("../../admin")
    assert recorder.requests[0].url.raw_path == b"/v1/google/search/..%2F..%2Fadmin"


def test_history_rejects_bad_artifact() -> None:
    client = make_client(Recorder(ok()))
    with pytest.raises(ValueError):
        client.google.search.get(REQUEST_ID, artifact="pdf")  # type: ignore[call-overload]


@pytest.mark.parametrize(
    ("status", "cls"),
    [
        (400, prismcrawl.BadRequestError),
        (401, prismcrawl.AuthenticationError),
        (402, prismcrawl.InsufficientCreditsError),
        (404, prismcrawl.NotFoundError),
        (405, prismcrawl.APIStatusError),
        (413, prismcrawl.PayloadTooLargeError),
        (500, prismcrawl.InternalServerError),
        (503, prismcrawl.InternalServerError),
    ],
)
def test_status_errors(status: int, cls: type) -> None:
    client = make_client(Recorder(error(status, "some_code", "Something failed")), max_retries=0)
    with pytest.raises(cls) as info:
        client.google.search(query="q")
    exc = info.value
    assert isinstance(exc, prismcrawl.APIStatusError)
    assert exc.status_code == status
    assert exc.code == "some_code"
    assert exc.message == "Something failed"
    assert exc.request_id == REQUEST_ID
    assert REQUEST_ID in str(exc)


def test_non_json_error_body() -> None:
    client = make_client(Recorder(httpx.Response(502, text="Bad Gateway")), max_retries=0)
    with pytest.raises(prismcrawl.InternalServerError) as info:
        client.google.search(query="q")
    assert info.value.body == "Bad Gateway"
    assert info.value.code is None


def test_rate_limit_error_fields() -> None:
    response = error(429, "rate_limited", "Slow down", rule="per_minute", reset_at="2999-01-01T00:00:00Z")
    recorder = Recorder(response)
    client = make_client(recorder)
    with pytest.raises(prismcrawl.RateLimitError) as info:
        client.google.search(query="q")
    assert info.value.rule == "per_minute"
    assert info.value.reset_at == "2999-01-01T00:00:00Z"
    # The limit resets too far in the future to wait for.
    assert len(recorder.requests) == 1


def test_retries_rate_limit_with_retry_after() -> None:
    recorder = Recorder(httpx.Response(429, headers={"retry-after": "0"}, json={}), ok())
    make_client(recorder).google.search(query="q")
    assert len(recorder.requests) == 2


def test_retries_rate_limit_with_unparseable_retry_after() -> None:
    recorder = Recorder(httpx.Response(429, headers={"retry-after": "soon"}, json={}), ok())
    make_client(recorder).google.search(query="q")
    assert len(recorder.requests) == 2


def test_retries_server_errors_then_gives_up() -> None:
    recorder = Recorder(error(500, "internal", "boom"))
    client = make_client(recorder, max_retries=3)
    with pytest.raises(prismcrawl.InternalServerError):
        client.google.search(query="q")
    assert len(recorder.requests) == 4


def test_retries_server_error_then_succeeds() -> None:
    recorder = Recorder(error(503, "unavailable", "busy"), ok())
    make_client(recorder).google.search(query="q")
    assert len(recorder.requests) == 2


def test_does_not_retry_client_errors() -> None:
    recorder = Recorder(error(400, "invalid_request", "query is required"))
    with pytest.raises(prismcrawl.BadRequestError):
        make_client(recorder).google.search(query="q")
    assert len(recorder.requests) == 1


def test_connect_error_is_retried_for_post() -> None:
    recorder = Recorder(httpx.ConnectError("refused"), ok())
    make_client(recorder).google.search(query="q")
    assert len(recorder.requests) == 2


def test_read_timeout_is_not_retried_for_post() -> None:
    recorder = Recorder(httpx.ReadTimeout("slow"), ok())
    with pytest.raises(prismcrawl.APITimeoutError):
        make_client(recorder).google.search(query="q")
    assert len(recorder.requests) == 1


def test_read_timeout_is_retried_for_get() -> None:
    recorder = Recorder(httpx.ReadTimeout("slow"), ok())
    make_client(recorder).google.search.get(REQUEST_ID)
    assert len(recorder.requests) == 2


def test_connection_error_wrapped() -> None:
    client = make_client(Recorder(httpx.ConnectError("refused")), max_retries=0)
    with pytest.raises(prismcrawl.APIConnectionError):
        client.google.search(query="q")


def test_token_pagination() -> None:
    recorder = Recorder(
        ok({"results": [1], "has_next_page": True, "next_page_token": "t1"}),
        ok({"results": [2], "has_next_page": True, "next_page_token": "t2"}),
        ok({"results": [3], "has_next_page": False}),
    )
    pages: List[Any] = list(make_client(recorder).google.maps.reviews.pages(id="place", sort_by="relevance"))
    assert [p["data"]["content"]["results"] for p in pages] == [[1], [2], [3]]
    assert [recorder.body(i).get("next_page_token") for i in range(3)] == [None, "t1", "t2"]
    assert all(recorder.body(i)["sort_by"] == "relevance" for i in range(3))


def test_page_pagination_and_max_pages() -> None:
    recorder = Recorder(ok({"results": [], "has_next_page": True}))
    pages = list(make_client(recorder).yelp.reviews.pages(id="biz", page=3, max_pages=3))
    assert len(pages) == 3
    assert [recorder.body(i)["page"] for i in range(3)] == [3, 4, 5]


def test_pagination_stops_without_token() -> None:
    recorder = Recorder(ok({"results": [], "has_next_page": True}))
    pages = list(make_client(recorder).google.maps.reviews.pages(id="place"))
    assert len(pages) == 1


def test_pagination_stops_for_html() -> None:
    body = {"success": True, "request_id": REQUEST_ID, "data": {"format": "html+br+base64", "content": "x"}}
    recorder = Recorder(httpx.Response(200, json=body))
    assert len(list(make_client(recorder).google.maps.reviews.pages(id="place", html=True))) == 1


def test_decode_html() -> None:
    encoded = base64.b64encode(brotli.compress(b"<html>caf\xc3\xa9</html>")).decode()
    response: Dict[str, Any] = {
        "success": True,
        "request_id": REQUEST_ID,
        "data": {"format": "html+br+base64", "content": encoded},
    }
    assert decode_html(response) == "<html>café</html>"
    assert decode_html(response["data"]) == "<html>café</html>"
    assert decode_html(encoded) == "<html>café</html>"
    with pytest.raises(ValueError):
        decode_html({"data": {"format": "json", "content": {}}})


def test_context_manager_closes_owned_client() -> None:
    with PrismCrawl(api_key="k") as client:
        http = client._http
    assert http.is_closed


def test_context_manager_leaves_user_client_open() -> None:
    http = httpx.Client()
    with PrismCrawl(api_key="k", http_client=http):
        pass
    assert not http.is_closed
    http.close()


def test_async_client() -> None:
    recorder = Recorder(error(500, "internal", "boom"), ok({"results": [1]}))

    async def run() -> Dict[str, Any]:
        async with make_async_client(recorder) as client:
            return await client.apple.app_store.search(query="notes")  # type: ignore[return-value]

    response = asyncio.run(run())
    assert response["data"]["content"]["results"] == [1]
    assert len(recorder.requests) == 2
    assert recorder.requests[-1].url.path == "/v1/apple/app-store/search"


def test_async_errors_and_history() -> None:
    recorder = Recorder(error(401, "invalid_api_key", "invalid api key"))

    async def run() -> None:
        async with make_async_client(recorder) as client:
            await client.google.search.get(REQUEST_ID)

    with pytest.raises(prismcrawl.AuthenticationError):
        asyncio.run(run())


def test_async_pagination() -> None:
    recorder = Recorder(
        ok({"has_next_page": True, "next_page_token": "t1"}),
        ok({"has_next_page": False}),
    )

    async def run() -> int:
        async with make_async_client(recorder) as client:
            return len([page async for page in client.tripadvisor.reviews.pages(id="123")])

    assert asyncio.run(run()) == 2
    assert recorder.body(1)["next_page_token"] == "t1"


def dummy(annotation: Any) -> Any:
    text = str(annotation)
    if "Coordinates" in text:
        return {"latitude": 1.0, "longitude": 2.0}
    if "int" in text:
        return 1
    return "x"


def endpoints(namespace: Any, path: str = "client") -> Iterator[Any]:
    for name, value in sorted(vars(namespace).items()):
        if name.startswith("_") or name == "bing":
            continue
        if isinstance(value, (SyncEndpoint, AsyncEndpoint)):
            yield f"{path}.{name}", value
            # Related endpoints nest under their parent, e.g. google.images.light.
            yield from endpoints(value, f"{path}.{name}")
        elif hasattr(value, "__dict__"):
            yield from endpoints(value, f"{path}.{name}")


def spec_post_paths() -> List[str]:
    return sorted(path for path, item in SPEC["paths"].items() if "post" in item)


def test_every_spec_endpoint_is_reachable() -> None:
    recorder = Recorder(ok())
    client = make_client(recorder)
    seen = []
    for _, endpoint in endpoints(client):
        params = inspect.signature(endpoint.__call__).parameters
        required = {name: dummy(p.annotation) for name, p in params.items() if p.default is inspect.Parameter.empty}
        endpoint(**required)
        seen.append(recorder.requests[-1].url.path)
        endpoint.get(REQUEST_ID)
        assert recorder.requests[-1].url.path == f"{seen[-1]}/{REQUEST_ID}"
    assert sorted(seen) == spec_post_paths()


def test_async_client_matches_sync_client() -> None:
    sync_paths = sorted(name for name, _ in endpoints(PrismCrawl(api_key="k")))
    async_paths = sorted(name for name, _ in endpoints(AsyncPrismCrawl(api_key="k")))
    assert sync_paths == async_paths
    assert len(sync_paths) == len(spec_post_paths())


def test_signatures_match_spec_required_fields() -> None:
    schemas = SPEC["components"]["schemas"]
    client = PrismCrawl(api_key="k")
    for _, endpoint in endpoints(client):
        op = SPEC["paths"][endpoint._path]["post"]
        schema = schemas[op["requestBody"]["content"]["application/json"]["schema"]["$ref"].rsplit("/", 1)[-1]]
        webhook = {"webhook_url", "webhook_secret"}
        params = inspect.signature(endpoint.__call__).parameters
        required = {n for n, p in params.items() if p.default is inspect.Parameter.empty}
        assert required == set(schema.get("required", [])), endpoint._path
        assert set(schema["properties"]) - webhook <= set(params), endpoint._path
        assert not webhook & set(params), endpoint._path
        submit = inspect.signature(endpoint.submit).parameters
        submit_required = {n for n, p in submit.items() if p.default is inspect.Parameter.empty}
        assert submit_required == set(schema.get("required", [])) | webhook, endpoint._path
        assert set(schema["properties"]) <= set(submit), endpoint._path


# Nested endpoints, async submission, request history, and webhooks.

JOB = "v3-" + "a" * 96
HOOK_URL = "https://example.com/hook"
HOOK_SECRET = "s" * 32


def receipt(status: str = "queued") -> httpx.Response:
    return httpx.Response(
        202,
        json={
            "success": True,
            "request_id": REQUEST_ID,
            "data": {
                "job_id": JOB,
                "status": status,
                "status_url": f"/v1/async/requests/{JOB}",
                "result_url": f"/v1/async/requests/{JOB}/result",
                "accepted_at": "2026-11-20T00:00:00Z",
                "result_expires_at": None,
                "result_status": None,
                "error": None,
                "webhook": {"status": "waiting", "attempts": 0, "response_status": 0},
            },
        },
    )


def test_nested_endpoints() -> None:
    recorder = Recorder(ok())
    client = make_client(recorder)
    client.google.images(query="q")
    assert recorder.requests[-1].url.path == "/v1/google/images"
    client.google.images.light(query="q")
    assert recorder.requests[-1].url.path == "/v1/google/images/light"
    client.google.ads.transparency.details(advertiser_id="a", creative_id="c")
    assert recorder.requests[-1].url.path == "/v1/google/ads/transparency/details"


def test_submit_sends_prefer_and_idempotency_key() -> None:
    recorder = Recorder(receipt())
    result = make_client(recorder).google.search.submit(query="q", webhook_url=HOOK_URL, webhook_secret=HOOK_SECRET)
    assert result["data"]["job_id"] == JOB
    request = recorder.requests[-1]
    assert request.headers["prefer"] == "respond-async"
    assert len(request.headers["idempotency-key"]) == 36
    assert recorder.body() == {"webhook_url": HOOK_URL, "webhook_secret": HOOK_SECRET, "query": "q"}


def test_submit_retries_dropped_connections_with_the_same_key() -> None:
    recorder = Recorder(httpx.ReadTimeout("slow"), receipt())
    make_client(recorder).yelp.reviews.submit(
        id="biz", idempotency_key="key-1", webhook_url=HOOK_URL, webhook_secret=HOOK_SECRET
    )
    assert [r.headers["idempotency-key"] for r in recorder.requests] == ["key-1", "key-1"]


def test_sync_calls_do_not_accept_webhook_fields() -> None:
    with pytest.raises(TypeError):
        make_client(Recorder(ok())).google.search(query="q", webhook_url=HOOK_URL)  # type: ignore[call-arg]


def test_async_jobs_status_and_result() -> None:
    recorder = Recorder(receipt("running"), ok())
    client = make_client(recorder)
    assert client.async_jobs.status(JOB)["data"]["status"] == "running"
    assert recorder.requests[-1].url.path == f"/v1/async/requests/{JOB}"
    client.async_jobs.result(JOB)
    assert recorder.requests[-1].url.path == f"/v1/async/requests/{JOB}/result"


def test_async_client_submit() -> None:
    recorder = Recorder(receipt())

    async def run() -> str:
        async with make_async_client(recorder) as client:
            response = await client.google.images.light.submit(
                query="q", webhook_url=HOOK_URL, webhook_secret=HOOK_SECRET
            )
            return response["data"]["job_id"]

    assert asyncio.run(run()) == JOB
    assert recorder.requests[-1].url.path == "/v1/google/images/light"


def history_page(cursor: Optional[str]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "success": True,
            "request_id": REQUEST_ID,
            "data": {"requests": [], "next_cursor": cursor, "range": {"from": "a", "to": "b"}},
        },
    )


def test_account_requests_pages_follow_next_cursor() -> None:
    recorder = Recorder(history_page("c2"), history_page(None))
    pages = list(make_client(recorder).account.requests.pages(provider="google", from_="2026-11-01T00:00:00Z"))
    assert len(pages) == 2
    first, second = recorder.requests
    assert first.url.path == "/v1/account/requests"
    assert first.url.params["provider"] == "google"
    assert first.url.params["from"] == "2026-11-01T00:00:00Z"
    assert "cursor" not in first.url.params
    assert second.url.params["cursor"] == "c2"


def test_account_requests_get() -> None:
    recorder = Recorder(ok())
    make_client(recorder).account.requests.get(REQUEST_ID)
    assert recorder.requests[-1].url.path == f"/v1/account/requests/{REQUEST_ID}"


SECRET = "w" * 40
PAYLOAD = json.dumps({"success": True, "request_id": REQUEST_ID, "data": {"format": "json", "content": {}}})
T = 1_800_000_000


def sign(body: str, ts: int = T, key: str = SECRET) -> str:
    digest = hmac.new(key.encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={digest}"


def webhook_headers(signature: str) -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Prism-Signature": signature,
        "Prism-Event-Id": REQUEST_ID,
        "Prism-Request-Id": REQUEST_ID,
        "Prism-Result-Status": "200",
    }


def test_verify_webhook_accepts_valid_deliveries() -> None:
    event = prismcrawl.verify_webhook(PAYLOAD, webhook_headers(sign(PAYLOAD)), SECRET, now=T)
    assert event.event_id == REQUEST_ID
    assert event.request_id == REQUEST_ID
    assert event.result_status == 200
    assert event.body["success"] is True
    event = prismcrawl.verify_webhook(PAYLOAD.encode(), httpx.Headers(webhook_headers(sign(PAYLOAD))), SECRET, now=T)
    assert event.timestamp == T


@pytest.mark.parametrize(
    ("payload", "headers", "secret", "now", "match"),
    [
        (PAYLOAD + " ", None, SECRET, T, "doesn't match"),
        (PAYLOAD, None, "x" * 40, T, "doesn't match"),
        (PAYLOAD, None, SECRET, T + 301, "tolerance"),
        (PAYLOAD, {"Prism-Event-Id": "e"}, SECRET, T, "Missing Prism-Signature"),
        (PAYLOAD, webhook_headers("t=1,v1=zz"), SECRET, T, "Malformed"),
    ],
)
def test_verify_webhook_rejects_bad_deliveries(
    payload: str, headers: Optional[Dict[str, str]], secret: str, now: int, match: str
) -> None:
    with pytest.raises(prismcrawl.WebhookVerificationError, match=match):
        prismcrawl.verify_webhook(payload, headers or webhook_headers(sign(PAYLOAD)), secret, now=now)
