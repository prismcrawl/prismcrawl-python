# PrismCrawl Python SDK

The official Python client for [PrismCrawl](https://www.prismcrawl.com): live search results, AI answers, products, places, and reviews returned as structured JSON. Pass your API key and every PrismCrawl endpoint is one method call away. See the [API reference](https://www.prismcrawl.com/docs) for every endpoint and parameter.

```python
from prismcrawl import PrismCrawl

client = PrismCrawl(api_key="YOUR_API_KEY")
results = client.google.search(query="best espresso machines")
```

> **You need a PrismCrawl API key.** Sign up at [prismcrawl.com](https://www.prismcrawl.com) and create a key in the dashboard. It's free, and you don't need a card.
>
> **Pricing:** at volume, prepaid credit packages bring the price as low as **$0.15 per 1,000 successful requests**, and failed requests are free. That's **100x cheaper than SerpApi**. See [pricing](#pricing).

## Why PrismCrawl

- **As low as $0.15 per 1,000 successful requests** at volume, 100x cheaper than SerpApi
- **You only pay for successes.** Failed requests are free.
- **Free to start:** 100 free credits, and you don't need a card
- **No subscription:** prepaid credit packages from $5, valid for 90 days
- **One key covers 26 endpoints:** Google, Bing, DuckDuckGo, Amazon, Google Maps, Apple Maps, Yelp, Tripadvisor, Google Play, and the Apple App Store
- **Answers from AI search engines:** Google AI Overviews, Google AI Mode, and Bing's AI overview with citations, at no additional charge
- **Live, uncached results:** every request fetches fresh data from the source
- **Proven at scale:** 99% successful response rate and more than 1 billion SERPs every month
- **See every request:** filter your request history in the [dashboard](https://www.prismcrawl.com) by query, provider, status, format, or date. You can check the parameters, timing, and credits for each request, copy it as cURL, rerun it, or download the saved HTML/JSON. Request details are kept for 90 days and the HTML/JSON for 30 days. To skip storing the results of a request, pass `zero_trace=True`.

## What it can do

- **Search:** Google (including AI Overviews, AI Mode, Shopping, and Local results), Bing (including its AI overview with citations), DuckDuckGo, and Amazon
- **Maps and places:** Google Maps, Bing Maps, Apple Maps, DuckDuckGo Maps, Yelp, and Tripadvisor
- **Reviews:** Google Maps, Google contributors, Yelp, Tripadvisor, Apple Maps, Google Play, and the Apple App Store
- **App stores:** Google Play (apps, games, books, movies) and the Apple App Store: search, product details, and reviews
- **Shopping:** Google Shopping product details and merchant offers

## SDK features

- Every endpoint, with sync and async clients
- Type hints for every parameter and response field, generated from the API spec
- Automatic retries for rate limits, server errors, and connection failures
- Page iterators for paginated endpoints
- Helpers for request history and source HTML

## Installation

```bash
pip install prismcrawl
```

Requires Python 3.9 or later.

## Quick start

Create an API key in the [PrismCrawl dashboard](https://www.prismcrawl.com). New accounts get 100 free credits.

```python
from prismcrawl import PrismCrawl

client = PrismCrawl(api_key="YOUR_API_KEY")

response = client.google.search(query="best espresso machines", gl="us")

for result in response["data"]["content"]["results"]:
    print(result["rank"], result["title"], result["url"])
```

If you don't pass `api_key`, the client reads the `PRISMCRAWL_API_KEY` environment variable:

```bash
export PRISMCRAWL_API_KEY="YOUR_API_KEY"
```

```python
client = PrismCrawl()
```

More complete, runnable scripts are in [`examples/`](https://github.com/prismcrawl/prismcrawl-python/tree/main/examples).

## Endpoints

Each endpoint is a callable object. Calling it runs the request. Every endpoint also has `.get(request_id)` to fetch a previous request, and paginated endpoints have `.pages(...)`.

| Method | API endpoint |
|---|---|
| `client.google.search(...)` | `POST /v1/google/search` |
| `client.google.maps.search(...)` | `POST /v1/google/maps/search` |
| `client.google.maps.reviews(...)` | `POST /v1/google/maps/reviews` |
| `client.google.contributor.reviews(...)` | `POST /v1/google/contributor/reviews` |
| `client.google.shopping.product(...)` | `POST /v1/google/shopping/product` |
| `client.google.play.apps.search(...)` | `POST /v1/google/play/apps/search` |
| `client.google.play.games.search(...)` | `POST /v1/google/play/games/search` |
| `client.google.play.books.search(...)` | `POST /v1/google/play/books/search` |
| `client.google.play.movies.search(...)` | `POST /v1/google/play/movies/search` |
| `client.google.play.product(...)` | `POST /v1/google/play/product` |
| `client.google.play.reviews(...)` | `POST /v1/google/play/reviews` |
| `client.bing.search(...)` | `POST /v1/microsoft/search` |
| `client.bing.maps.search(...)` | `POST /v1/microsoft/maps/search` |
| `client.duckduckgo.search(...)` | `POST /v1/duckduckgo/search` |
| `client.duckduckgo.maps.search(...)` | `POST /v1/duckduckgo/maps/search` |
| `client.amazon.search(...)` | `POST /v1/amazon/search` |
| `client.apple.maps.search(...)` | `POST /v1/apple/maps/search` |
| `client.apple.maps.reviews(...)` | `POST /v1/apple/maps/reviews` |
| `client.apple.app_store.search(...)` | `POST /v1/apple/app-store/search` |
| `client.apple.app_store.product(...)` | `POST /v1/apple/app-store/product` |
| `client.apple.app_store.reviews(...)` | `POST /v1/apple/app-store/reviews` |
| `client.yelp.search(...)` | `POST /v1/yelp/search` |
| `client.yelp.reviews(...)` | `POST /v1/yelp/reviews` |
| `client.tripadvisor.search(...)` | `POST /v1/tripadvisor/search` |
| `client.tripadvisor.place(...)` | `POST /v1/tripadvisor/place` |
| `client.tripadvisor.reviews(...)` | `POST /v1/tripadvisor/reviews` |

`client.bing` and `client.microsoft` are the same namespace. The API paths use `microsoft`.

Parameter names match the [API reference](https://www.prismcrawl.com/docs) exactly. Your editor shows each parameter's type and description.

```python
places = client.google.maps.search(
    query="coffee shop",
    coordinates={"latitude": 30.2672, "longitude": -97.7431},
    zoom=14,
)

reviews = client.google.maps.reviews(id="ChIJ...", limit=20)

products = client.amazon.search(query="espresso machine")
```

## AI answers

Google AI Overviews and Bing's AI overview come back in `serp_features` with type `ai_summary`. For Google's AI Mode, pass `udm=50`:

```python
response = client.google.search(query="compare electric cars for a family", udm=50)

data = response["data"]
if data["format"] == "json":
    for feature in data["content"]["serp_features"]:
        if feature["type"] == "ai_summary":
            print(feature)
```

## Pagination

Paginated endpoints have a `.pages()` iterator that takes the same parameters. It follows `next_page_token` (or `page`) until `has_next_page` is false.

```python
for page in client.yelp.reviews.pages(id="halcyon-austin-2", max_pages=5):
    for review in page["data"]["content"]["results"]:
        print(review["rating"], review["text"][:80])
```

Each page is a separate request and uses one credit. Use `max_pages` to cap spending.

## Request history

Every response includes a `request_id`. Fetch a previous request with `.get()` on the endpoint that made it:

```python
response = client.google.search(query="best espresso machines")
request_id = response["request_id"]

metadata = client.google.search.get(request_id)
archived = client.google.search.get(request_id, artifact="json")  # parsed response
source = client.google.search.get(request_id, artifact="html")  # source HTML, as str
```

A new request can take a few seconds to appear in history. Until then, `.get()` raises `NotFoundError`.

Requests made with `zero_trace=True` aren't archived. For those, `.get()` returns only the status code and whether a credit was charged.

## Source HTML

Pass `html=True` to get the provider's original page instead of parsed JSON. The API returns it as Base64-encoded Brotli, and `decode_html` converts it back to a string:

```bash
pip install "prismcrawl[html]"
```

```python
from prismcrawl import decode_html

response = client.google.search(query="best espresso machines", html=True)
html = decode_html(response)
```

## Async

`AsyncPrismCrawl` has the same interface, with `await` in front of each call:

```python
import asyncio
from prismcrawl import AsyncPrismCrawl


async def main() -> None:
    async with AsyncPrismCrawl() as client:
        google, bing = await asyncio.gather(
            client.google.search(query="best espresso machines"),
            client.bing.search(query="best espresso machines"),
        )
        async for page in client.tripadvisor.reviews.pages(id="...", max_pages=3):
            ...


asyncio.run(main())
```

## Errors

Every exception inherits from `prismcrawl.PrismCrawlError`. API errors carry the status code, the error `code`, and the `request_id` to give support.

```python
import prismcrawl

try:
    client.google.search(query="best espresso machines")
except prismcrawl.RateLimitError as error:
    print("Rate limited until", error.reset_at)
except prismcrawl.InsufficientCreditsError:
    print("Out of credits")
except prismcrawl.APIStatusError as error:
    print(error.status_code, error.code, error.message, error.request_id)
except prismcrawl.APIConnectionError:
    print("Could not reach PrismCrawl")
```

| Status | Exception |
|---|---|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 402 | `InsufficientCreditsError` |
| 404 | `NotFoundError` |
| 413 | `PayloadTooLargeError` |
| 429 | `RateLimitError` |
| 5xx | `InternalServerError` |
| other | `APIStatusError` |
| no response | `APIConnectionError`, `APITimeoutError` |

Failed requests don't use credits.

## Retries and timeouts

The client retries up to 2 times, with exponential backoff, on:

- 429 responses, waiting until the limit resets if that's within 30 seconds
- 5xx responses
- connection failures

It never retries a search after the request was sent and the connection dropped, because the search may have completed and used a credit.

```python
client = PrismCrawl(max_retries=5, timeout=60.0)

# Per-request timeout
client.google.search(query="...", timeout=10.0)
```

The default timeout is 120 seconds.

## Configuration

```python
import httpx
from prismcrawl import PrismCrawl

client = PrismCrawl(
    api_key="YOUR_API_KEY",
    base_url="https://api.prismcrawl.com",  # or PRISMCRAWL_BASE_URL
    timeout=120.0,
    max_retries=2,
    default_headers={"x-my-header": "value"},
    http_client=httpx.Client(proxy="http://localhost:8080"),
)
```

If the API adds a parameter before this SDK does, pass it with `extra_body`:

```python
client.google.search(query="...", extra_body={"new_param": True})
```

## Types

Responses are plain `dict`s. `prismcrawl.types` has a `TypedDict` for every request and response, so editors and type checkers know their shape:

```python
from prismcrawl.types import GoogleJsonSearchResponse, SearchResult
```

## Pricing

Each successful request uses one PrismCrawl credit. Failed requests are free. Fetching another page is a separate request and uses a credit, including each page from `.pages()`.

- 100 free credits for new accounts
- Prepaid credit packages from $5, with no subscription
- As low as $0.15 per 1,000 successful requests at volume, 100x cheaper than SerpApi
- Credits are valid for 90 days

See [prismcrawl.com](https://www.prismcrawl.com) for current pricing.

## Development

The endpoint classes and types come from the API's OpenAPI spec. To regenerate them:

```bash
python scripts/generate.py --fetch   # download the latest spec, then regenerate
python scripts/generate.py           # regenerate from openapi.json
```

Run the checks:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest mypy ruff brotli
pytest && mypy && ruff check . && ruff format --check .
```

## Resources

- [PrismCrawl](https://www.prismcrawl.com): sign up, create API keys, and view your request history
- [API reference](https://www.prismcrawl.com/docs): every endpoint and parameter
- [Examples](https://github.com/prismcrawl/prismcrawl-python/tree/main/examples): runnable scripts for common tasks
- [TypeScript SDK](https://github.com/prismcrawl/prismcrawl-node)
- [MCP server](https://www.prismcrawl.com/mcp): connect Claude, Cursor, and other AI assistants to PrismCrawl ([GitHub](https://github.com/prismcrawl/prismcrawl-mcp))

## Support

Email support@prismcrawl.com. To report a bug in this SDK, [open an issue](https://github.com/prismcrawl/prismcrawl-python/issues).

## License

MIT
