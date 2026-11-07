"""Daily USAspending pipeline: fetch current fiscal year, load to RAW, build dbt (dev)."""

from datetime import datetime, timedelta
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

# dags/ -> orchestration/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

LEVELS = ["awards", "transactions"]
STATES = ["SD", "IA", "NE", "MN", "IL"]
AWARD_TYPES = ["contracts", "grants"]

# Federal fiscal year starts Oct 1, so today + 3 months lands in the FY's year.
# BSD date syntax (macOS); the GitHub Linux runner uses `date -d "+3 months"`.
FISCAL_YEAR = "$(date -v+3m +%Y)"

FETCH_COMMANDS = [
    f"uv run python ingestion/usaspending.py --level {level} --state {state} "
    f"--fiscal-year {FISCAL_YEAR} --award-type {award_type}"
    for level in LEVELS
    for state in STATES
    for award_type in AWARD_TYPES
]

with DAG(
    dag_id="usaspending_daily",
    schedule="@daily",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
    tags=["usaspending"],
):
    fetch = BashOperator.partial(
        task_id="fetch",
        cwd=str(REPO_ROOT),
        max_active_tis_per_dagrun=4,
    ).expand(bash_command=FETCH_COMMANDS)

    load_awards = BashOperator(
        task_id="load_awards",
        cwd=str(REPO_ROOT),
        bash_command="uv run python ingestion/load_usaspending.py --level awards",
    )

    load_transactions = BashOperator(
        task_id="load_transactions",
        cwd=str(REPO_ROOT),
        bash_command="uv run python ingestion/load_usaspending.py --level transactions",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        cwd=str(REPO_ROOT / "transform"),
        bash_command="uv run dbt build",
    )

    fetch >> load_awards >> load_transactions >> dbt_build
