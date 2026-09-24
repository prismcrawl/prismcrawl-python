# Examples

Runnable scripts for common PrismCrawl tasks. Each one reads your API key from `PRISMCRAWL_API_KEY`, and most take an optional query argument.

```bash
pip install prismcrawl
export PRISMCRAWL_API_KEY="YOUR_API_KEY"
python examples/quickstart.py "best espresso machines"
```

| Script | What it shows | Credits |
|---|---|---|
| [`quickstart.py`](quickstart.py) | Google search, printing the organic results | 1 |
| [`local_reviews.py`](local_reviews.py) | Find a place on Google Maps, then page through its reviews | 3 |
| [`app_research.py`](app_research.py) | App Store search, product details, and a review rating breakdown | 3 |
| [`compare_engines.py`](compare_engines.py) | Google, Bing, and DuckDuckGo concurrently with the async client | 3 |
| [`save_html.py`](save_html.py) | Save a results page's source HTML, then look it up in history. Needs `pip install "prismcrawl[html]"` | 1 |
