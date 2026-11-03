"""Snowflake connection helper for the ingestion pipeline."""

import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv


def get_connection() -> snowflake.connector.SnowflakeConnection:
    """Open a Snowflake connection using key-pair auth from environment variables."""
    load_dotenv()
    key_path = Path(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]).expanduser()

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        authenticator="SNOWFLAKE_JWT",
        private_key_file=str(key_path),
        private_key_file_pwd=os.environ["SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"],
        enable_server_session_keep_alive_auto_detection=False,
    )


def main() -> None:
    """Check the connection by asking Snowflake who we are."""
    with get_connection() as connection:
        row = connection.cursor().execute(
            "select current_user(), current_role(), current_warehouse(), "
            "current_database(), current_schema()"
        ).fetchone()

    print(row)


if __name__ == "__main__":
    main()