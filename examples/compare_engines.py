"""Run the same query on Google, Bing, and DuckDuckGo at once and compare the results.

Uses the async client to send the three requests concurrently.

    python examples/compare_engines.py "best hiking boots"
"""

import asyncio
import sys
from typing import Any, List, Mapping

from prismcrawl import AsyncPrismCrawl


def domains(response: Mapping[str, Any]) -> List[str]:
    data = response["data"]
    if data["format"] != "json":
        return []
    return [r["domain"] for r in data["content"]["results"] if r.get("type") == "organic" and r.get("domain")]


async def main(query: str) -> None:
    async with AsyncPrismCrawl() as client:
        google, bing, duckduckgo = await asyncio.gather(
            client.google.search(query=query),
            client.bing.search(query=query),
            client.duckduckgo.search(query=query),
        )

    results = {
        "Google": domains(google),
        "Bing": domains(bing),
        "DuckDuckGo": domains(duckduckgo),
    }
    for engine, found in results.items():
        print(f"{engine:>10}: {', '.join(found[:5])}")

    shared = set.intersection(*(set(found) for found in results.values()))
    print(f"\nIn all three: {', '.join(sorted(shared)) or 'none'}")


asyncio.run(main(" ".join(sys.argv[1:]) or "best hiking boots"))
