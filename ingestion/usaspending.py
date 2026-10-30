"""Fetch award data from the USAspending API."""

import json
from pathlib import Path

import httpx

API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
REQUEST_FILE = Path(__file__).parent / "sample_grant_search.json"


def fetch_page(client: httpx.Client, body: dict, page: int) -> dict:
    """Request one page of award results."""
    request_body = {**body, "page": page}
    response = client.post(API_URL, json=request_body)
    response.raise_for_status()
    return response.json()


def main() -> None:
    body = json.loads(REQUEST_FILE.read_text())

    with httpx.Client(timeout=60) as client:
        data = fetch_page(client, body, page=1)

    print(f"Results on this page: {len(data['results'])}")
    print(f"More pages available: {data['page_metadata']['hasNext']}")


if __name__ == "__main__":
    main()