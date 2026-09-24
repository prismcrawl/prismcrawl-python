"""Search Google and print the organic results.

export PRISMCRAWL_API_KEY="YOUR_API_KEY"
python examples/quickstart.py "best espresso machines"
"""

import sys

from prismcrawl import PrismCrawl

query = " ".join(sys.argv[1:]) or "best espresso machines"

with PrismCrawl() as client:
    response = client.google.search(query=query, gl="us")

data = response["data"]
if data["format"] != "json":
    raise SystemExit("Expected JSON results")

for result in data["content"]["results"]:
    if result["type"] == "organic":
        print(f"{result['rank']:>2}. {result['title']}\n    {result['url']}")

print(f"\nrequest_id: {response['request_id']}")
