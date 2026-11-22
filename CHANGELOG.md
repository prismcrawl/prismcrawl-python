# Changelog

## 0.2.0

- Every current PrismCrawl endpoint: 127 endpoints across 21 sources, up from 26, including Google Flights, Hotels, Scholar, Trends, Shopping, Jobs, and Lens, YouTube, Walmart, eBay, Home Depot, Zillow, and more
- Related endpoints nest under their parent, such as `client.google.images.light(...)` alongside `client.google.images(...)`
- `.submit()` on every endpoint for background requests with signed webhooks, with idempotency keys and safe retries
- `verify_webhook()` to check `Prism-Signature` on webhook deliveries
- `client.async_jobs.status()` and `client.async_jobs.result()` for background jobs
- `client.account.requests.list()`, `.pages()`, and `.get()` to search request history across endpoints
- Google Search accepts `url` in place of `query`
- `webhook_url` and `webhook_secret` are accepted only by `.submit()`

## 0.1.0

First release.

- `PrismCrawl` and `AsyncPrismCrawl` clients for every PrismCrawl API endpoint
- Typed parameters and `TypedDict` response types generated from the OpenAPI spec
- `.get(request_id)` for request history and archived artifacts
- `.pages()` iterators for paginated endpoints
- `decode_html()` for `html=True` responses
- Automatic retries for rate limits, server errors, and connection failures
