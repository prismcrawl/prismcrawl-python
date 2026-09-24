"""Save the source HTML of a search results page, then look the request up in history.

Needs the optional Brotli dependency: pip install "prismcrawl[html]"

    python examples/save_html.py "best espresso machines"
"""

import sys
import time
from pathlib import Path

import prismcrawl
from prismcrawl import PrismCrawl, decode_html

query = " ".join(sys.argv[1:]) or "best espresso machines"

with PrismCrawl() as client:
    response = client.google.search(query=query, html=True)
    html = decode_html(response)
    path = Path("results.html")
    path.write_text(html, encoding="utf-8")
    print(f"Saved {len(html):,} characters to {path}")

    # New requests take a few seconds to show up in history.
    request_id = response["request_id"]
    for _ in range(10):
        try:
            history = client.google.search.get(request_id)
            break
        except prismcrawl.NotFoundError:
            time.sleep(3)
    else:
        raise SystemExit("Request not in history yet; try again shortly")

meta = history["data"]
print(f"Request {request_id}: status {meta.get('status_code')}, took {meta.get('duration_ms')} ms")
