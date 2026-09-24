"""Look up an app on the Apple App Store: search, product details, and recent reviews.

python examples/app_research.py "weather"
"""

import sys
from collections import Counter

from prismcrawl import PrismCrawl

query = " ".join(sys.argv[1:]) or "weather"

with PrismCrawl() as client:
    search = client.apple.app_store.search(query=query, country="us", limit=5)
    if search["data"]["format"] != "json" or not search["data"]["content"]["results"]:
        raise SystemExit("No apps found")

    print("Top results:")
    for app in search["data"]["content"]["results"]:
        print(f"  {app['title']} by {app.get('developer', '?')} (id {app['id']})")

    app_id = search["data"]["content"]["results"][0].get("id")
    if not app_id:
        raise SystemExit("Top result has no id")
    product = client.apple.app_store.product(id=app_id, country="us")
    reviews = client.apple.app_store.reviews(id=app_id, country="us")

if product["data"]["format"] == "json" and product["data"]["content"]["results"]:
    details = product["data"]["content"]["results"][0]
    print(f"\n{details['title']}: rated {details.get('rating', '?')}, price {details.get('price', '?')}")

if reviews["data"]["format"] == "json":
    stars = Counter(r["rating"] for r in reviews["data"]["content"]["results"] if r.get("rating") is not None)
    print("\nRecent review ratings:")
    for rating in sorted(stars, reverse=True):
        print(f"  {rating:.0f}★ {'#' * stars[rating]} {stars[rating]}")
