# USAspending API exploration

Exploration done before writing any ingestion code, to understand how the
data is structured and which filters the pipeline needs. All requests were
made with curl against the public USAspending API (v2), which requires no key.

## Endpoints tested

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v2/references/toptier_agencies/` | GET | List of top-level federal agencies with budget figures |
| `/api/v2/search/spending_by_award/` | POST | Search individual awards using filters |

Sample request bodies are saved in `ingestion/sample_award_search.json`
(contracts) and `ingestion/sample_grant_search.json` (grants).

## Finding 1: Award vs. transaction grain

The time period filter returns any award with activity in that period, not
awards that started in it. A FY2025 search returned awards that began in 2023.
`Award Amount` is the lifetime total of the award, not the amount spent in the
period searched. Summing award amounts by year would overstate spending.

## Finding 2: Grants carry most infrastructure money

For DOT work performed in South Dakota in FY2025, the largest contract was
about $2 million, while the largest grant was about $63 million. Most highway
and bridge funding flows to the state as grants, and the state then hires
contractors. A contracts-only pipeline would miss most of the money.

## Finding 3: Use generated_internal_id as the key

`Award ID` is the agency's own reference number and is not guaranteed to be
unique across agencies. `generated_internal_id` combines several identifiers
and is unique. Its prefix also shows the award type: `CONT_AWD` for contracts,
`ASST_` for assistance such as grants.

## Finding 4: Results are paginated

Each response returns one page of results, with `page_metadata.hasNext`
showing whether more exist. Ingestion has to loop through pages until
`hasNext` is false.

## Finding 5: Place of performance vs. recipient location

Filtering by place of performance returns work done in South Dakota, even when
the recipient is based elsewhere (for example, a Utah firm). For this project,
where the work happens matters more than where the firm is headquartered.

## Finding 6: Missing start dates

Four of the five largest grants had a null `Start Date`. Award-level dates are
not reliable for measuring when money was spent.

## Finding 7: Recipients of grants are states, not firms

Every top grant went to the State of South Dakota. Firms hired by the state
with that money do not appear as federal recipients. Some of that activity may
be available as subaward data, which needs separate exploration.

## Other observations

- Codes such as `toptier_code` ("069") are text, not numbers. Storing them as
  numbers would drop leading zeros and break joins.
- Money values arrive as floating-point numbers and should be converted to an
  exact decimal type during transformation.
- Award IDs embed codes such as the state abbreviation. What other embedded
  codes mean should be confirmed against agency documentation before use.
- The API can be slow to respond, so every request needs a timeout.
- Searches only go back to 2007-10-01, which covers the FY2019 start date.

## Decisions this leads to

1. Pull both contracts (A, B, C, D) and grants (02, 03, 04, 05).
2. Build the fact table at transaction grain, so spending can be measured by
   when each action happened rather than by award totals.
3. Use `generated_internal_id` as the award key.
4. Filter by place of performance for the five Midwest states.
5. Store all codes and IDs as text, and money as exact decimals.
6. Handle pagination and timeouts in the ingestion script.
7. Scope business question 3 to firms winning federal contracts, and explore
   subaward data separately before expanding it.