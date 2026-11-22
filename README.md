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
- **One key covers 127 endpoints across 21 sources:** Google, Bing, Amazon, Apple, YouTube, Walmart, eBay, Home Depot, DuckDuckGo, Yahoo, Yandex, Baidu, Naver, Brave, Yelp, Tripadvisor, OpenTable, Airbnb, Zillow, Instagram, and Facebook
- **Answers from AI search engines:** Google AI Overviews, Google AI Mode (with follow-up questions), Bing Copilot, Brave AI Mode, and Naver AI Mode, at no additional charge
- **Live, uncached results:** every request fetches fresh data from the source
- **Proven at scale:** 99% successful response rate and more than 1 billion SERPs every month
- **See every request:** filter your request history in the [dashboard](https://www.prismcrawl.com) by query, provider, status, format, or date. You can check the parameters, timing, and credits for each request, copy it as cURL, rerun it, or download the saved HTML/JSON. Request details are kept for 90 days and the HTML/JSON for 30 days. To skip storing the results of a request, pass `zero_trace=True`.

## What it can do

- **Search:** Google (including AI Overviews, AI Mode, Light, Forums, News, Images, Videos, Short Videos, Lens, and reverse image search), Bing (including Copilot, News, Images, and Videos), DuckDuckGo, Yahoo, Yandex, Baidu, Naver, and Brave
- **Maps and places:** Google Maps (search, directions, photos, posts, and reviews), Bing Maps, Apple Maps, DuckDuckGo Maps, Yelp, Tripadvisor, and OpenTable
- **Shopping:** Google Shopping, Amazon, Walmart, eBay, Home Depot, and Bing Shopping, with product details, sellers, and reviews
- **Travel:** Google Flights, Hotels, and Travel Explore, Airbnb, and Zillow listings
- **Research and data:** Google Scholar, Patents, Trends, Finance, Jobs, Events, Sports, and Ads Transparency
- **Video and social:** YouTube search, channels, videos, and transcripts, plus Instagram and Facebook profiles
- **App stores:** Google Play (apps, games, books, movies) and the Apple App Store: search, product details, and reviews
- **Google links:** decode Google `/goto` and `/url` result links into their destinations

## SDK features

- Every endpoint, with sync and async clients
- Type hints for every parameter and response field, generated from the API spec
- Automatic retries for rate limits, server errors, and connection failures
- Page iterators for paginated endpoints
- Markdown output and `json_restrictor` field selection
- Background requests with signed webhooks, and a `verify_webhook()` helper
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

Each endpoint is a callable object. Calling it runs the request. Every endpoint also has `.submit(...)` to run it in the background and `.get(request_id)` to fetch a previous request, and paginated endpoints (marked ⋯ below) have `.pages(...)`.

Some endpoints have related endpoints under them: `client.google.images(...)` runs Google Images, and `client.google.images.light(...)` runs Google Images Light.

<details>
<summary><strong>Google</strong> (67)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.google.about_this_result(...)` | `POST /v1/google/about-this-result` | Google About This Result |
| `client.google.ads(...)` | `POST /v1/google/ads` | Google Ads |
| `client.google.ads.transparency(...)` ⋯ | `POST /v1/google/ads/transparency` | Google Ads Transparency |
| `client.google.ads.transparency.details(...)` | `POST /v1/google/ads/transparency/details` | Google Ads Transparency Ad Details |
| `client.google.ai_mode(...)` | `POST /v1/google/ai-mode` | Google AI Mode |
| `client.google.ai_overview(...)` | `POST /v1/google/ai-overview` | Google AI Overview |
| `client.google.autocomplete(...)` | `POST /v1/google/autocomplete` | Google Autocomplete |
| `client.google.contributor.reviews(...)` ⋯ | `POST /v1/google/contributor/reviews` | Google Contributor Reviews |
| `client.google.decode(...)` | `POST /v1/google/decode` | Google Link Decoder |
| `client.google.events(...)` | `POST /v1/google/events` | Google Events |
| `client.google.finance(...)` | `POST /v1/google/finance` | Google Finance |
| `client.google.finance.markets(...)` | `POST /v1/google/finance/markets` | Google Finance Markets |
| `client.google.flights.autocomplete(...)` | `POST /v1/google/flights/autocomplete` | Google Flights Autocomplete |
| `client.google.flights.deals(...)` | `POST /v1/google/flights/deals` | Google Flights Deals |
| `client.google.flights.search(...)` | `POST /v1/google/flights/search` | Google Flights |
| `client.google.forums(...)` ⋯ | `POST /v1/google/forums` | Google Forums |
| `client.google.hotels.autocomplete(...)` | `POST /v1/google/hotels/autocomplete` | Google Hotels Autocomplete |
| `client.google.hotels.photos(...)` ⋯ | `POST /v1/google/hotels/photos` | Google Hotels Photos |
| `client.google.hotels.reviews(...)` ⋯ | `POST /v1/google/hotels/reviews` | Google Hotels Reviews |
| `client.google.hotels.search(...)` ⋯ | `POST /v1/google/hotels/search` | Google Hotels |
| `client.google.images(...)` ⋯ | `POST /v1/google/images` | Google Images |
| `client.google.images.light(...)` ⋯ | `POST /v1/google/images/light` | Google Images Light |
| `client.google.images.related_content(...)` | `POST /v1/google/images/related-content` | Google Images Related Content |
| `client.google.jobs(...)` ⋯ | `POST /v1/google/jobs` | Google Jobs |
| `client.google.jobs.listing(...)` | `POST /v1/google/jobs/listing` | Google Jobs Listing |
| `client.google.lens(...)` | `POST /v1/google/lens` | Google Lens |
| `client.google.light.search(...)` ⋯ | `POST /v1/google/light/search` | Google Light Search |
| `client.google.local(...)` | `POST /v1/google/local` | Google Local |
| `client.google.local.services(...)` | `POST /v1/google/local/services` | Google Local Services |
| `client.google.maps.autocomplete(...)` | `POST /v1/google/maps/autocomplete` | Google Maps Autocomplete |
| `client.google.maps.directions(...)` | `POST /v1/google/maps/directions` | Google Maps Directions |
| `client.google.maps.photos(...)` ⋯ | `POST /v1/google/maps/photos` | Google Maps Photos |
| `client.google.maps.photos.meta(...)` | `POST /v1/google/maps/photos/meta` | Google Maps Photo Metadata |
| `client.google.maps.posts(...)` ⋯ | `POST /v1/google/maps/posts` | Google Maps Posts |
| `client.google.maps.reviews(...)` ⋯ | `POST /v1/google/maps/reviews` | Google Maps Reviews |
| `client.google.maps.search(...)` | `POST /v1/google/maps/search` | Search Google Maps |
| `client.google.news(...)` ⋯ | `POST /v1/google/news` | Google News |
| `client.google.news.light(...)` ⋯ | `POST /v1/google/news/light` | Google News Light |
| `client.google.patents.details(...)` | `POST /v1/google/patents/details` | Google Patents Details |
| `client.google.patents.search(...)` ⋯ | `POST /v1/google/patents/search` | Google Patents |
| `client.google.play.apps.search(...)` ⋯ | `POST /v1/google/play/apps/search` | Google Play Apps |
| `client.google.play.books.search(...)` ⋯ | `POST /v1/google/play/books/search` | Google Play Books |
| `client.google.play.games.search(...)` ⋯ | `POST /v1/google/play/games/search` | Google Play Games |
| `client.google.play.movies.search(...)` ⋯ | `POST /v1/google/play/movies/search` | Google Play Movies |
| `client.google.play.product(...)` | `POST /v1/google/play/product` | Google Play Product |
| `client.google.play.reviews(...)` ⋯ | `POST /v1/google/play/reviews` | Google Play Reviews |
| `client.google.related_questions(...)` ⋯ | `POST /v1/google/related-questions` | Google Related Questions |
| `client.google.reverse_image(...)` | `POST /v1/google/reverse-image` | Google Reverse Image |
| `client.google.scholar.author(...)` ⋯ | `POST /v1/google/scholar/author` | Google Scholar Author |
| `client.google.scholar.case_law(...)` ⋯ | `POST /v1/google/scholar/case-law` | Google Scholar Case Law |
| `client.google.scholar.cite(...)` | `POST /v1/google/scholar/cite` | Google Scholar Cite |
| `client.google.scholar.search(...)` ⋯ | `POST /v1/google/scholar/search` | Google Scholar |
| `client.google.search(...)` | `POST /v1/google/search` | Search Google |
| `client.google.shopping(...)` ⋯ | `POST /v1/google/shopping` | Google Shopping |
| `client.google.shopping.filters(...)` | `POST /v1/google/shopping/filters` | Google Shopping Filters |
| `client.google.shopping.immersive_product(...)` ⋯ | `POST /v1/google/shopping/immersive-product` | Google Immersive Product |
| `client.google.shopping.light(...)` ⋯ | `POST /v1/google/shopping/light` | Google Shopping Light |
| `client.google.shopping.product(...)` | `POST /v1/google/shopping/product` | Google Shopping Product |
| `client.google.short_videos(...)` ⋯ | `POST /v1/google/short-videos` | Google Short Videos |
| `client.google.sports(...)` | `POST /v1/google/sports` | Google Sports |
| `client.google.travel.explore(...)` | `POST /v1/google/travel/explore` | Google Travel Explore |
| `client.google.trends(...)` | `POST /v1/google/trends` | Google Trends |
| `client.google.trends.autocomplete(...)` | `POST /v1/google/trends/autocomplete` | Google Trends Autocomplete |
| `client.google.trends.news(...)` | `POST /v1/google/trends/news` | Google Trends News |
| `client.google.trends.trending_now(...)` | `POST /v1/google/trends/trending-now` | Google Trends Trending Now |
| `client.google.videos(...)` ⋯ | `POST /v1/google/videos` | Google Videos |
| `client.google.videos.light(...)` ⋯ | `POST /v1/google/videos/light` | Google Videos Light |

</details>

<details>
<summary><strong>Airbnb</strong> (1)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.airbnb.search(...)` ⋯ | `POST /v1/airbnb/search` | Airbnb Search |

</details>

<details>
<summary><strong>Amazon</strong> (3)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.amazon.autocomplete(...)` | `POST /v1/amazon/autocomplete` | Amazon Autocomplete |
| `client.amazon.product(...)` | `POST /v1/amazon/product` | Amazon Product |
| `client.amazon.search(...)` ⋯ | `POST /v1/amazon/search` | Search Amazon |

</details>

<details>
<summary><strong>Apple</strong> (6)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.apple.app_store.product(...)` | `POST /v1/apple/app-store/product` | Apple App Store Product |
| `client.apple.app_store.reviews(...)` ⋯ | `POST /v1/apple/app-store/reviews` | Apple App Store Reviews |
| `client.apple.app_store.search(...)` ⋯ | `POST /v1/apple/app-store/search` | Apple App Store Search |
| `client.apple.maps.place(...)` | `POST /v1/apple/maps/place` | Apple Maps Places |
| `client.apple.maps.reviews(...)` | `POST /v1/apple/maps/reviews` | Apple Maps Reviews |
| `client.apple.maps.search(...)` | `POST /v1/apple/maps/search` | Apple Maps Search |

</details>

<details>
<summary><strong>Baidu</strong> (2)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.baidu.news.search(...)` ⋯ | `POST /v1/baidu/news/search` | Baidu News |
| `client.baidu.search(...)` ⋯ | `POST /v1/baidu/search` | Baidu Search |

</details>

<details>
<summary><strong>Bing</strong> (9)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.bing.copilot(...)` | `POST /v1/microsoft/copilot` | Bing Copilot |
| `client.bing.images.reverse(...)` ⋯ | `POST /v1/microsoft/images/reverse` | Bing Reverse Image |
| `client.bing.images.search(...)` ⋯ | `POST /v1/microsoft/images/search` | Bing Images |
| `client.bing.maps.search(...)` | `POST /v1/microsoft/maps/search` | Bing Maps |
| `client.bing.news.search(...)` ⋯ | `POST /v1/microsoft/news/search` | Bing News |
| `client.bing.search(...)` ⋯ | `POST /v1/microsoft/search` | Search Bing |
| `client.bing.shopping.product(...)` | `POST /v1/microsoft/shopping/product` | Bing Product |
| `client.bing.shopping.search(...)` ⋯ | `POST /v1/microsoft/shopping/search` | Bing Shopping |
| `client.bing.videos.search(...)` ⋯ | `POST /v1/microsoft/videos/search` | Bing Videos |

</details>

<details>
<summary><strong>Brave</strong> (1)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.brave.ai_mode(...)` ⋯ | `POST /v1/brave/ai-mode` | Brave AI Mode |

</details>

<details>
<summary><strong>DuckDuckGo</strong> (4)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.duckduckgo.maps.search(...)` | `POST /v1/duckduckgo/maps/search` | DuckDuckGo Maps |
| `client.duckduckgo.news.search(...)` ⋯ | `POST /v1/duckduckgo/news/search` | DuckDuckGo News |
| `client.duckduckgo.search(...)` ⋯ | `POST /v1/duckduckgo/search` | DuckDuckGo Search |
| `client.duckduckgo.search.light(...)` ⋯ | `POST /v1/duckduckgo/search/light` | DuckDuckGo Light |

</details>

<details>
<summary><strong>Facebook</strong> (1)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.facebook.profile(...)` | `POST /v1/facebook/profile` | Facebook Profile |

</details>

<details>
<summary><strong>Home Depot</strong> (3)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.home_depot.product(...)` | `POST /v1/home-depot/product` | Home Depot Product |
| `client.home_depot.reviews(...)` ⋯ | `POST /v1/home-depot/reviews` | Home Depot Reviews |
| `client.home_depot.search(...)` ⋯ | `POST /v1/home-depot/search` | Home Depot Search |

</details>

<details>
<summary><strong>Instagram</strong> (1)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.instagram.profile(...)` ⋯ | `POST /v1/instagram/profile` | Instagram Profile |

</details>

<details>
<summary><strong>Naver</strong> (3)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.naver.ai_mode(...)` | `POST /v1/naver/ai-mode` | Naver AI Mode |
| `client.naver.ai_overview(...)` | `POST /v1/naver/ai-overview` | Naver AI Overview |
| `client.naver.search(...)` ⋯ | `POST /v1/naver/search` | Naver Search |

</details>

<details>
<summary><strong>OpenTable</strong> (1)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.opentable.reviews(...)` ⋯ | `POST /v1/opentable/reviews` | OpenTable Reviews |

</details>

<details>
<summary><strong>Tripadvisor</strong> (3)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.tripadvisor.place(...)` | `POST /v1/tripadvisor/place` | Tripadvisor Place |
| `client.tripadvisor.reviews(...)` ⋯ | `POST /v1/tripadvisor/reviews` | Tripadvisor Reviews |
| `client.tripadvisor.search(...)` ⋯ | `POST /v1/tripadvisor/search` | Tripadvisor Search |

</details>

<details>
<summary><strong>Walmart</strong> (4)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.walmart.product(...)` | `POST /v1/walmart/product` | Walmart Product |
| `client.walmart.product.sellers(...)` | `POST /v1/walmart/product/sellers` | Walmart Sellers |
| `client.walmart.reviews(...)` ⋯ | `POST /v1/walmart/reviews` | Walmart Reviews |
| `client.walmart.search(...)` ⋯ | `POST /v1/walmart/search` | Walmart Search |

</details>

<details>
<summary><strong>Yahoo</strong> (4)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.yahoo.images.search(...)` ⋯ | `POST /v1/yahoo/images/search` | Yahoo Images |
| `client.yahoo.search(...)` ⋯ | `POST /v1/yahoo/search` | Yahoo Search |
| `client.yahoo.trends(...)` ⋯ | `POST /v1/yahoo/trends` | Yahoo Trends |
| `client.yahoo.videos.search(...)` ⋯ | `POST /v1/yahoo/videos/search` | Yahoo Videos |

</details>

<details>
<summary><strong>Yandex</strong> (3)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.yandex.images.search(...)` ⋯ | `POST /v1/yandex/images/search` | Yandex Images |
| `client.yandex.search(...)` ⋯ | `POST /v1/yandex/search` | Yandex Search |
| `client.yandex.videos.search(...)` ⋯ | `POST /v1/yandex/videos/search` | Yandex Videos |

</details>

<details>
<summary><strong>Yelp</strong> (3)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.yelp.place(...)` | `POST /v1/yelp/place` | Yelp Place |
| `client.yelp.reviews(...)` ⋯ | `POST /v1/yelp/reviews` | Yelp Reviews |
| `client.yelp.search(...)` ⋯ | `POST /v1/yelp/search` | Yelp Search |

</details>

<details>
<summary><strong>YouTube</strong> (4)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.youtube.channel(...)` ⋯ | `POST /v1/youtube/channel` | YouTube Channel |
| `client.youtube.search(...)` ⋯ | `POST /v1/youtube/search` | YouTube Search |
| `client.youtube.transcript(...)` | `POST /v1/youtube/transcript` | YouTube Video Transcript |
| `client.youtube.video(...)` ⋯ | `POST /v1/youtube/video` | YouTube Video |

</details>

<details>
<summary><strong>Zillow</strong> (1)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.zillow.search(...)` ⋯ | `POST /v1/zillow/search` | Zillow Search |

</details>

<details>
<summary><strong>eBay</strong> (3)</summary>

| Method | API endpoint | Description |
|---|---|---|
| `client.ebay.product(...)` | `POST /v1/ebay/product` | eBay Product |
| `client.ebay.search(...)` ⋯ | `POST /v1/ebay/search` | eBay Search |
| `client.ebay.seller(...)` ⋯ | `POST /v1/ebay/seller` | eBay Seller |

</details>

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

Google AI Overviews and Bing's AI overview come back in `serp_features` with type `ai_summary`. Google AI Mode has its own endpoint, and supports follow-up questions:

```python
first = client.google.ai_mode(query="compare electric cars for a family", continuable=True)

token = first["data"]["content"].get("subsequent_request_token")
if token:
    client.google.ai_mode(query="which has the most cargo space?", subsequent_request_token=token)
```

Follow-up tokens expire after 15 minutes. `client.naver.ai_mode` works the same way.

## Markdown and field selection

Pass `output="md"` to get Markdown instead of JSON, or `json_restrictor` to return only the fields you need:

```python
md = client.google.search(query="best espresso machines", output="md")
print(md["data"]["content"])  # a Markdown string

urls = client.google.search(query="best espresso machines", json_restrictor="results[].{title,url}")
print(urls["data"]["content"])  # only the selected fields
```

To paginate with `json_restrictor`, include `next_page_token` in the selection.

## Google result links

Google sometimes returns a result whose destination it hasn't revealed yet. Its `url` is then a Google `/goto` or `/url` link. Decode up to 10 of them per request:

```python
decoded = client.google.decode(urls=["https://www.google.com/url?..."])
```

Each decoded batch uses one credit.

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

Search your history across every endpoint with `client.account.requests`:

```python
recent = client.account.requests.list(provider="google", status="failure", limit=20)

for page in client.account.requests.pages(from_="2026-11-01T00:00:00Z"):
    for request in page["data"]["requests"]:
        print(request["request_id"])
```

`from_` is sent as the API's `from` filter.

Requests made with `zero_trace=True` aren't archived. For those, `.get()` returns only the status code and whether a credit was charged.

## Background requests and webhooks

`.submit()` runs any endpoint in the background. PrismCrawl accepts the job right away, runs it, and POSTs the completed response to your webhook, signed with your secret. Results are kept for one hour after completion, so they survive disconnects.

```python
receipt = client.google.search.submit(
    query="best espresso machines",
    webhook_url="https://example.com/prismcrawl-webhook",
    webhook_secret=os.environ["PRISMCRAWL_WEBHOOK_SECRET"],  # 32 to 256 printable ASCII characters
)
print(receipt["data"]["job_id"], receipt["data"]["status"])
```

Each submission has an `Idempotency-Key`. The SDK generates one; pass `idempotency_key=` to choose your own, and reuse it with the same parameters to retry a submission safely. A receipt means the job was accepted, not that the search succeeded.

Verify each delivery with `verify_webhook`, using the raw request body. For example, with Flask:

```python
import os

from flask import Flask, request
from prismcrawl import WebhookVerificationError, verify_webhook

app = Flask(__name__)


@app.post("/prismcrawl-webhook")
def prismcrawl_webhook():
    try:
        event = verify_webhook(request.get_data(), request.headers, os.environ["PRISMCRAWL_WEBHOOK_SECRET"])
    except WebhookVerificationError:
        return "", 400
    # event.body is the endpoint's response; event.result_status is its HTTP status.
    # Retries reuse event.event_id, so skip events you've already handled.
    return "", 204
```

It rejects bad signatures and timestamps older than five minutes. Respond with a 2xx within 10 seconds; failed deliveries are retried for up to an hour without running the search again.

For troubleshooting, `client.async_jobs.status(job_id)` and `client.async_jobs.result(job_id)` read a job directly. Don't poll them more often than every five seconds. Background requests can't use `zero_trace`.

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

Errors don't use credits.

## Retries and timeouts

The client retries up to 2 times, with exponential backoff, on:

- 429 responses, waiting until the limit resets if that's within 30 seconds
- 5xx responses
- connection failures

It never retries a search after the request was sent and the connection dropped, because the search may have completed and used a credit. `.submit()` is the exception: its `Idempotency-Key` makes resending safe, so it retries those too.

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

Each completed request uses one PrismCrawl credit, including searches that come back with no results. Errors are free. Fetching another page is a separate request and uses a credit, including each page from `.pages()`.

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
