"""Load raw USAspending JSON Lines files into Snowflake."""

from pathlib import Path

from snowflake_client import get_connection

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "usaspending"

SETUP_STATEMENTS = [
    "create stage if not exists usaspending_stage file_format = (type = 'json')",
    """
    create table if not exists awards (
        record variant,
        source_file varchar,
        loaded_at timestamp_tz default current_timestamp()
    )
    """,
]

COPY_STATEMENT = """
copy into awards (record, source_file)
from (select $1, metadata$filename from @usaspending_stage)
on_error = 'abort_statement'
"""


def main() -> None:
    files = sorted(RAW_DIR.glob("*.jsonl"))
    if not files:
        raise SystemExit(f"No files found in {RAW_DIR}")

    with get_connection() as connection:
        cursor = connection.cursor()

        for statement in SETUP_STATEMENTS:
            cursor.execute(statement)

        for path in files:
            cursor.execute(f"put file://{path} @usaspending_stage auto_compress=true")
            print(f"Uploaded {path.name}")

        for row in cursor.execute(COPY_STATEMENT).fetchall():
            print(row)

        count = cursor.execute("select count(*) from awards").fetchone()[0]
        print(f"Rows in RAW.USASPENDING.AWARDS: {count}")


if __name__ == "__main__":
    main()