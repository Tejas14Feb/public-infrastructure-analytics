"""Fetch award data from the USAspending API and save it as raw JSON Lines."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "usaspending"
PAGE_SIZE = 100
MAX_PAGES = 50
PAUSE_SECONDS = 0.5

# New: award type names mapped to USAspending's codes
AWARD_TYPE_CODES = {
    "contracts": ["A", "B", "C", "D"],
    "grants": ["02", "03", "04", "05"],
}

FIELDS = ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Start Date"]


# New: convert a fiscal year into its start and end dates
def fiscal_year_dates(fiscal_year: int) -> tuple[str, str]:
    """Return the start and end dates of a federal fiscal year."""
    return f"{fiscal_year - 1}-10-01", f"{fiscal_year}-09-30"


# New: build the request body from arguments instead of a JSON file
def build_request_body(state: str, fiscal_year: int, award_type: str, agency: str) -> dict:
    """Build the award search filters for one state, fiscal year, and award type."""
    start_date, end_date = fiscal_year_dates(fiscal_year)
    return {
        "filters": {
            "award_type_codes": AWARD_TYPE_CODES[award_type],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": agency}],
            "place_of_performance_locations": [{"country": "USA", "state": state}],
            "time_period": [{"start_date": start_date, "end_date": end_date}],
        },
        "fields": FIELDS,
        "sort": "Award Amount",
        "order": "desc",
    }


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


# Changed: the filename and every record now include the request parameters
def save_records(records: list[dict], output_dir: Path, metadata: dict) -> Path:
    """Save records as JSON Lines, tagging each record with how it was fetched."""
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_at = datetime.now(timezone.utc)
    name = f"awards_{metadata['_state']}_fy{metadata['_fiscal_year']}_{metadata['_award_type']}"
    path = output_dir / f"{name}_{extracted_at:%Y%m%dT%H%M%SZ}.jsonl"

    with path.open("w") as file:
        for record in records:
            row = {**record, **metadata, "_extracted_at": extracted_at.isoformat()}
            file.write(json.dumps(row) + "\n")

    return path


# New: read and validate command-line arguments
def parse_args() -> argparse.Namespace:
    """Read the state, fiscal year, award type, and agency from the command line."""
    parser = argparse.ArgumentParser(
        description="Fetch USAspending awards and save them as raw JSON Lines."
    )
    parser.add_argument("--state", required=True, help="Two-letter state code, e.g. SD")
    parser.add_argument("--fiscal-year", type=int, required=True, help="e.g. 2025")
    parser.add_argument(
        "--award-type", required=True, choices=sorted(AWARD_TYPE_CODES),
        help="contracts or grants",
    )
    parser.add_argument(
        "--agency", default="Department of Transportation",
        help="Awarding agency name (default: Department of Transportation)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = args.state.upper()
    body = build_request_body(state, args.fiscal_year, args.award_type, args.agency)
    metadata = {
        "_state": state,
        "_fiscal_year": args.fiscal_year,
        "_award_type": args.award_type,
        "_agency": args.agency,
    }

    with httpx.Client(timeout=60) as client:
        records = fetch_all(client, body)

    print(f"Total records: {len(records)}")
    path = save_records(records, OUTPUT_DIR, metadata)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()