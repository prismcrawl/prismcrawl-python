"""Find a place on Google Maps, then read and summarize its reviews.

Shows passing an id from one endpoint to another, and paginating with .pages().

    python examples/local_reviews.py "coffee shop"
"""

import sys
from collections import Counter

from prismcrawl import PrismCrawl
from prismcrawl.types import Coordinates

query = " ".join(sys.argv[1:]) or "coffee shop"
austin: Coordinates = {"latitude": 30.2672, "longitude": -97.7431}

with PrismCrawl() as client:
    places = client.google.maps.search(query=query, coordinates=austin)
    if places["data"]["format"] != "json" or not places["data"]["content"]["results"]:
        raise SystemExit("No places found")

    place = places["data"]["content"]["results"][0]
    place_id = place.get("place_id")
    if not place_id:
        raise SystemExit(f"{place['title']} has no place_id")
    print(f"{place['title']} ({place.get('address') or 'no address'})\n")

    # Each page is a separate request and uses one credit, so cap it.
    ratings: Counter[float] = Counter()
    for page in client.google.maps.reviews.pages(id=place_id, limit=10, max_pages=2):
        if page["data"]["format"] != "json":
            break
        for review in page["data"]["content"]["results"]:
            rating = review.get("rating")
            if rating is None:
                continue
            ratings[rating] += 1
            text = (review.get("text") or "").replace("\n", " ")
            print(f"  {rating:.0f}★  {text[:90]}")

total = sum(ratings.values())
if total:
    average = sum(stars * count for stars, count in ratings.items()) / total
    print(f"\n{total} reviews, average {average:.2f}★")
