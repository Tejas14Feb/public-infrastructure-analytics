"""Load raw USAspending JSON Lines files into Snowflake."""

import argparse
from pathlib import Path

from snowflake_client import get_connection

RAW_ROOT = Path(__file__).parent.parent / "data" / "raw" / "usaspending"

# Each level loads from its own folder, through its own stage, into its own table
LEVELS = {
    "awards": {"stage": "usaspending_stage", "table": "awards"},
    "transactions": {"stage": "usaspending_transactions_stage", "table": "transactions"},
}


def setup_statements(stage: str, table: str) -> list[str]:
    """Return the statements that create the stage and table if they don't exist."""
    return [
        f"create stage if not exists {stage} file_format = (type = 'json')",
        f"""
        create table if not exists {table} (
            record variant,
            source_file varchar,
            loaded_at timestamp_tz default current_timestamp()
        )
        """,
    ]


def copy_statement(stage: str, table: str) -> str:
    """Return the COPY INTO statement that loads staged files into the table.

    purge = true deletes each file from the stage after it loads, so old files
    can't be reloaded if the table's load history is ever reset.
    """
    return f"""
    copy into {table} (record, source_file)
    from (select $1, metadata$filename from @{stage})
    on_error = 'abort_statement'
    purge = true
    """


def parse_args() -> argparse.Namespace:
    """Read which level to load from the command line."""
    parser = argparse.ArgumentParser(description="Load raw USAspending files into Snowflake.")
    parser.add_argument(
        "--level", default="awards", choices=sorted(LEVELS),
        help="awards or transactions (default: awards)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stage = LEVELS[args.level]["stage"]
    table = LEVELS[args.level]["table"]
    raw_dir = RAW_ROOT / args.level

    files = sorted(raw_dir.glob("*.jsonl"))
    if not files:
        raise SystemExit(f"No files found in {raw_dir}")

    with get_connection() as connection:
        cursor = connection.cursor()

        for statement in setup_statements(stage, table):
            cursor.execute(statement)

        for path in files:
            cursor.execute(f"put file://{path} @{stage} auto_compress=true")
            print(f"Uploaded {path.name}")

        for row in cursor.execute(copy_statement(stage, table)).fetchall():
            print(row)

        count = cursor.execute(f"select count(*) from {table}").fetchone()[0]
        print(f"Rows in RAW.USASPENDING.{table.upper()}: {count}")


if __name__ == "__main__":
    main()