"""Unit tests for building USAspending requests."""

from usaspending import build_request_body, fiscal_year_dates


def test_fiscal_year_runs_october_to_september():
    assert fiscal_year_dates(2025) == ("2024-10-01", "2025-09-30")


def test_request_filters_by_state_and_fiscal_year():
    body = build_request_body("SD", 2025, "grants", "Department of Transportation")
    filters = body["filters"]

    assert filters["place_of_performance_locations"] == [{"country": "USA", "state": "SD"}]
    assert filters["time_period"] == [{"start_date": "2024-10-01", "end_date": "2025-09-30"}]


def test_award_types_map_to_usaspending_codes():
    contracts = build_request_body("IA", 2024, "contracts", "Department of Transportation")
    grants = build_request_body("IA", 2024, "grants", "Department of Transportation")

    assert contracts["filters"]["award_type_codes"] == ["A", "B", "C", "D"]
    assert grants["filters"]["award_type_codes"] == ["02", "03", "04", "05"]



def test_transaction_requests_use_transaction_fields_and_sort():
    body = build_request_body("SD", 2025, "grants", "Department of Transportation", level="transactions")

    assert "Transaction Amount" in body["fields"]
    assert "Action Date" in body["fields"]
    assert body["sort"] == "Transaction Amount"