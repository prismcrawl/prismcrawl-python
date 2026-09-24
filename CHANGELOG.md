# Changelog

## 0.1.0

First release.

- `PrismCrawl` and `AsyncPrismCrawl` clients for every PrismCrawl API endpoint
- Typed parameters and `TypedDict` response types generated from the OpenAPI spec
- `.get(request_id)` for request history and archived artifacts
- `.pages()` iterators for paginated endpoints
- `decode_html()` for `html=True` responses
- Automatic retries for rate limits, server errors, and connection failures
