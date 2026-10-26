# Public Infrastructure Analytics

An analytics engineering pipeline that tracks public infrastructure spending across the Midwest, built with dbt and Snowflake.

## Business questions

1. Where is infrastructure money going in South Dakota, Iowa, Nebraska, Minnesota, and Illinois, by state, sector, and agency?
2. How has spending changed since the 2021 infrastructure bill?
3. Which firms win the most contracts in the region?
4. What upcoming opportunities are open right now? *(planned)*

## Data sources

- **USAspending.gov** – federal contracts and grants, updated daily
- **U.S. Census Bureau** – monthly public construction spending
- **SAM.gov** – open contract opportunities *(planned)*

## Tech stack

- **Python** with uv for ingestion
- **dbt Core** for transformation and testing
- **Snowflake** as the data warehouse
- **Airflow** for orchestration *(planned)*
- **GitHub Actions** for CI/CD *(planned)*
- **Tableau Public** for the dashboard *(planned)*

## Project structure

| Folder | Purpose |
|---|---|
| `ingestion/` | Pulls raw data from public APIs |
| `transform/` | dbt models, tests, and docs |
| `orchestration/` | Scheduling and pipeline runs |
| `docs/` | Architecture notes and decision log |
| `tests/` | Tests for the Python code |

## Status

In active development.