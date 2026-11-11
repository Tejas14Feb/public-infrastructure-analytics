"""Unit tests for exporting reporting marts to CSV."""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from export_reporting_marts import export_mart, load_private_key


class FakeCursor:
    """Stands in for a Snowflake cursor: execute, description, iteration."""

    description = [("STATE_CODE",), ("NET_OBLIGATIONS",)]

    def execute(self, sql):
        self.sql = sql

    def __iter__(self):
        return iter([("SD", 100.0), ("NE", 250.5)])


def test_export_mart_writes_lowercase_header_and_rows(tmp_path):
    cursor = FakeCursor()
    rows = export_mart(cursor, "mart_x", tmp_path)
    lines = (tmp_path / "mart_x.csv").read_text().splitlines()

    assert cursor.sql == "select * from analytics.prod.mart_x"
    assert rows == 2
    assert lines == ["state_code,net_obligations", "SD,100.0", "NE,250.5"]


def test_load_private_key_decrypts_encrypted_pem_to_der():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b"test-pass"),
    ).decode()

    der = load_private_key(pem, "test-pass")

    assert der[:1] == b"\x30"  # DER-encoded keys start with a SEQUENCE byte (0x30)
