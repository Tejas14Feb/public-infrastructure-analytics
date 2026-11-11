"""Export the reporting marts from ANALYTICS.PROD to CSV for Tableau Public."""

import csv
import os
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization

MARTS = (
    "mart_spending_by_state_sector",
    "mart_spending_trends",
    "mart_top_contract_recipients",
)
OUT_DIR = Path(__file__).resolve().parent / "data"


def load_private_key(pem: str, passphrase: str | None) -> bytes:
    """Decrypt a PEM private key and return unencrypted DER bytes."""
    key = serialization.load_pem_private_key(
        pem.encode(), password=passphrase.encode() if passphrase else None
    )
    return key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_connection() -> snowflake.connector.SnowflakeConnection:
    """Open a Snowflake connection as the dbt service user."""
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["DBT_SNOWFLAKE_USER"],
        role=os.environ["DBT_SNOWFLAKE_ROLE"],
        warehouse=os.environ["DBT_SNOWFLAKE_WAREHOUSE"],
        authenticator="SNOWFLAKE_JWT",
        private_key=load_private_key(
            os.environ["DBT_SNOWFLAKE_PRIVATE_KEY"],
            os.environ.get("DBT_SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"),
        ),
    )


def export_mart(cursor, mart: str, out_dir: Path) -> int:
    """Write one mart to <out_dir>/<mart>.csv and return the row count."""
    cursor.execute(f"select * from analytics.prod.{mart}")
    path = out_dir / f"{mart}.csv"
    rows = 0
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([col[0].lower() for col in cursor.description])
        for row in cursor:
            writer.writerow(row)
            rows += 1
    return rows


def main() -> None:
    """Export every reporting mart and print row counts."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        cursor = connection.cursor()
        for mart in MARTS:
            print(f"{mart}: {export_mart(cursor, mart, OUT_DIR)} rows")


if __name__ == "__main__":
    main()
