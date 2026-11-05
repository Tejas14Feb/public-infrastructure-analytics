"""Fetch award or transaction data from the USAspending API and save it as raw JSON Lines."""

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

API_BASE = "https://api.usaspending.gov/api/v2/search"
RAW_ROOT = Path(__file__).parent.parent / "data" / "raw" / "usaspending"
PAGE_SIZE = 100
MAX_PAGES = 200
PAUSE_SECONDS = 0.5
MAX_ATTEMPTS = 5
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

AWARD_TYPE_CODES = {
    "contracts": ["A", "B", "C", "D"],
    "grants": ["02", "03", "04", "05"],
}

# Everything that differs between the two levels lives here
LEVELS = {
    "awards": {
        "search_url": f"{API_BASE}/spending_by_award/",
        "count_url": f"{API_BASE}/spending_by_award_count/",
        "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Start Date"],
        "sort": "Award Amount",
    },
    "transactions": {
        "search_url": f"{API_BASE}/spending_by_transaction/",
        "count_url": f"{API_BASE}/spending_by_transaction_count/",
        "fields": [
            "Award ID", "Mod", "Recipient Name", "Recipient UEI", "Action Date",
            "Transaction Amount", "Awarding Agency", "Awarding Sub Agency",
            "Award Type", "Assistance Listing",
        ],
        "sort": "Transaction Amount",
    },
}

logger = logging.getLogger(__name__)


def fiscal_year_dates(fiscal_year: int) -> tuple[str, str]:
    """Return the start and end dates of a federal fiscal year."""
    return f"{fiscal_year - 1}-10-01", f"{fiscal_year}-09-30"


def build_filters(state: str, fiscal_year: int, award_type: str, agency: str) -> dict:
    """Build the search filters for one state, fiscal year, and award type."""
    start_date, end_date = fiscal_year_dates(fiscal_year)
    return {
        "award_type_codes": AWARD_TYPE_CODES[award_type],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": agency}],
        "place_of_performance_locations": [{"country": "USA", "state": state}],
        "time_period": [{"start_date": start_date, "end_date": end_date}],
    }


def build_request_body(
    state: str, fiscal_year: int, award_type: str, agency: str, level: str = "awards"
) -> dict:
    """Build the full search request for one level, state, fiscal year, and award type."""
    config = LEVELS[level]
    return {
        "filters": build_filters(state, fiscal_year, award_type, agency),
        "fields": config["fields"],
        "sort": config["sort"],
        "order": "desc",
    }


def post_with_retries(client: httpx.Client, url: str, payload: dict) -> dict:
    """POST a request, retrying timeouts, dropped connections, and 429/5xx responses."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.post(url, json=payload)
        except httpx.TransportError as error:
            reason = type(error).__name__
        else:
            if response.status_code not in RETRYABLE_STATUS_CODES:
                response.raise_for_status()
                return response.json()
            reason = f"HTTP {response.status_code}"

        if attempt == MAX_ATTEMPTS:
            raise RuntimeError(f"Request to {url} failed after {MAX_ATTEMPTS} attempts ({reason})")

        wait_seconds = 2**attempt
        logger.warning(
            "Attempt %s failed (%s), retrying in %ss", attempt, reason, wait_seconds,
        )
        time.sleep(wait_seconds)


def fetch_page(client: httpx.Client, url: str, body: dict, page: int) -> dict:
    """Request one page of results."""
    return post_with_retries(client, url, {**body, "page": page, "limit": PAGE_SIZE})


def fetch_all(client: httpx.Client, url: str, body: dict) -> list[dict]:
    """Fetch every page of results and return all records."""
    records: list[dict] = []
    page = 1

    while page <= MAX_PAGES:
        data = fetch_page(client, url, body, page)
        records.extend(data["results"])
        logger.info("Page %s: %s records", page, len(data["results"]))

        if not data["page_metadata"]["hasNext"]:
            break

        page += 1
        time.sleep(PAUSE_SECONDS)

    if page > MAX_PAGES:
        raise RuntimeError(
            f"Reached the {MAX_PAGES}-page limit before the last page. "
            "Refusing to save incomplete data."
        )

    return records


def get_expected_count(client: httpx.Client, url: str, filters: dict, award_type: str) -> int:
    """Return how many records the API says match, for reconciliation."""
    return post_with_retries(client, url, {"filters": filters})["results"][award_type]


def save_records(records: list[dict], output_dir: Path, level: str, metadata: dict) -> Path:
    """Save records as JSON Lines, tagging each record with how it was fetched."""
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_at = datetime.now(timezone.utc)
    name = f"{level}_{metadata['_state']}_fy{metadata['_fiscal_year']}_{metadata['_award_type']}"
    path = output_dir / f"{name}_{extracted_at:%Y%m%dT%H%M%SZ}.jsonl"

    with path.open("w") as file:
        for record in records:
            row = {**record, **metadata, "_extracted_at": extracted_at.isoformat()}
            file.write(json.dumps(row) + "\n")

    return path


def parse_args() -> argparse.Namespace:
    """Read the level, state, fiscal year, award type, and agency from the command line."""
    parser = argparse.ArgumentParser(
        description="Fetch USAspending awards or transactions and save them as raw JSON Lines."
    )
    parser.add_argument(
        "--level", default="awards", choices=sorted(LEVELS),
        help="awards or transactions (default: awards)",
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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    args = parse_args()
    config = LEVELS[args.level]
    state = args.state.upper()
    body = build_request_body(state, args.fiscal_year, args.award_type, args.agency, args.level)
    metadata = {
        "_state": state,
        "_fiscal_year": args.fiscal_year,
        "_award_type": args.award_type,
        "_agency": args.agency,
    }

    with httpx.Client(timeout=60) as client:
        expected = get_expected_count(client, config["count_url"], body["filters"], args.award_type)
        logger.info("Expected %s %s", expected, args.level)
        records = fetch_all(client, config["search_url"], body)

    # Reconciliation: the fetched count must match the API's count
    if len(records) != expected:
        raise RuntimeError(
            f"Reconciliation failed: expected {expected} {args.level}, fetched {len(records)}. "
            "Refusing to save."
        )

    logger.info("Total records: %s (matches expected count)", len(records))
    path = save_records(records, RAW_ROOT / args.level, args.level, metadata)
    logger.info("Saved to %s", path)


if __name__ == "__main__":
    main()