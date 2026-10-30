"""Fetch award data from the USAspending API."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx

API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
REQUEST_FILE = Path(__file__).parent / "sample_grant_search.json"
PAGE_SIZE = 100
MAX_PAGES = 50
PAUSE_SECONDS = 0.5
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "usaspending"


def fetch_page(client: httpx.Client, body: dict, page: int) -> dict:
    """Request one page of award results."""
    request_body = {**body, "page": page, "limit": PAGE_SIZE}
    response = client.post(API_URL, json=request_body)
    response.raise_for_status()
    return response.json()

def fetch_all(client: httpx.Client, body: dict) -> list[dict]:
    """Fetch every page of results and return all records."""
    records: list[dict] = []
    page = 1

    while page <= MAX_PAGES:
        data = fetch_page(client, body, page)
        records.extend(data["results"])
        print(f"Page {page}: {len(data['results'])} records")

        if not data["page_metadata"]["hasNext"]:
            break

        page += 1
        time.sleep(PAUSE_SECONDS)

    if page > MAX_PAGES:
        print(f"Warning: stopped at {MAX_PAGES} pages, more data may exist")

    return records

def save_records(records: list[dict], output_dir: Path) -> Path:
    """Save records as JSON Lines, one record per line."""
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_at = datetime.now(timezone.utc)
    path = output_dir / f"awards_{extracted_at:%Y%m%dT%H%M%SZ}.jsonl"

    with path.open("w") as file:
        for record in records:
            row = {**record, "_extracted_at": extracted_at.isoformat()}
            file.write(json.dumps(row) + "\n")

    return path

def main() -> None:
    body = json.loads(REQUEST_FILE.read_text())

    with httpx.Client(timeout=60) as client:
        records = fetch_all(client, body)

    print(f"Total records: {len(records)}")
    path = save_records(records, OUTPUT_DIR)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()