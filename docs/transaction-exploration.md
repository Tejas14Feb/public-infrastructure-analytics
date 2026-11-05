# USAspending transaction exploration

Explored after building the award-level staging model, which revealed that
award grain can't measure spending by year: `Award Amount` is an award's
lifetime total, so summing it by fiscal year overstates spending.

## Endpoints tested

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v2/search/spending_by_transaction/` | POST | One row per transaction (action) on an award |
| `/api/v2/search/spending_by_transaction_count/` | POST | Count of matching transactions by award category |

Sample request: `ingestion/sample_transaction_search.json` (DOT grants, South
Dakota, FY2025, the same search used in the award exploration).

## Findings

1. **Transactions place money in time.** Each has its own `Action Date` and
   `Transaction Amount`. The largest SD award ($62.6M) was a single Mod 0
   transaction dated 2025-08-11.
2. **Modifications add money to existing awards.** For example, a Mod 2
   transaction added $13.7M to an earlier grant.
3. **Negative transactions exist (de-obligations).** The largest was -$3.06M.
   All negatives were modifications, never Mod 0. Summing transactions gives
   net obligations.
4. **Old awards keep changing.** An award originating around 2021 had a -$2.1M
   modification in FY2025. Transaction grain attributes only that amount to
   FY2025.
5. **Mod numbers are inconsistent text** (`"0"`, `"00"`, `"2"`). They must stay
   strings and be normalized before comparing.
6. **Recipient names vary for the same entity** (`STATE OF SOUTH DAKOTA` vs
   `STATE OF SOUTH DAKOTA DEPARTMENT OF TRANSPORTATION`).
7. **There is no transaction ID.** Each row includes `generated_internal_id`,
   which links to the award, but no field uniquely identifies the transaction.
8. **Award types distinguish formula and project grants**, such as
   `FORMULA GRANT (A)` and `PROJECT GRANT (B)`.
9. **Award ID formats vary** across systems, reinforcing `generated_internal_id`
   as the award key.
10. **Pagination metadata differs** from the award search (`next`, `previous`,
    `hasPrevious`), but `hasNext` still works.
11. **Volume is manageable.** 1,382 transactions vs 1,136 awards for the same
    search, about 1.2 per award, so even Illinois should stay well under the
    API's 50,000-row limit.

## Decisions this leads to

1. Ingest transactions alongside awards, and build the fact table from
   transactions so spending can be measured by action date.
2. Keep the award staging model as the basis for an award dimension.
3. Allow negative amounts in transaction tests; they are real de-obligations.
4. Keep `Mod` as text, and normalize it before any "original award" logic.
5. Use formula vs project grant type as an analysis dimension, especially for
   changes after the 2021 infrastructure bill.
6. Use the count endpoint to reconcile expected vs fetched rows on every run,
   and fail if they don't match.

## Open questions

- **What uniquely identifies a transaction?** Candidates combine
  `generated_internal_id`, `Mod`, `Action Date`, and `Transaction Amount`. A
  uniqueness test in the staging model will confirm or reject this with real data.