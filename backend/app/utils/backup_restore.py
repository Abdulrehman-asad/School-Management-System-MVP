"""
Generic, engine-agnostic database backup/restore.

Rather than shelling out to `mysqldump` (which would only work against MySQL
and wouldn't be testable in this environment), this walks SQLAlchemy's table
metadata directly — export dumps every table to JSON in FK-safe dependency
order, restore reloads them the same way inside a single transaction. Works
identically whether the database is MySQL (production) or SQLite (local dev).
"""

import json
from datetime import date, datetime, time as time_type
from decimal import Decimal
from io import BytesIO
from typing import Dict, Any

from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy.types import DateTime, Date, Time

from app.database.session import Base, engine


def _json_default(obj):
    if isinstance(obj, (datetime, date, time_type)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _coerce_row_for_insert(table, row: dict) -> dict:
    """
    JSON round-trips temporal values as ISO strings (see _json_default above).
    Going through the ORM, SQLAlchemy's type layer would convert those back
    automatically — but Core's insert() with raw dicts does not, and SQLite's
    DBAPI in particular rejects a plain string for a DateTime/Date/Time column
    outright. Convert each value back to the real Python type its column
    expects before binding, based on the table's own schema (not guessing).
    """
    coerced = {}
    for col in table.columns:
        if col.name not in row:
            continue
        value = row[col.name]
        if value is None:
            coerced[col.name] = None
            continue
        if isinstance(col.type, DateTime) and isinstance(value, str):
            coerced[col.name] = datetime.fromisoformat(value)
        elif isinstance(col.type, Date) and isinstance(value, str):
            coerced[col.name] = date.fromisoformat(value)
        elif isinstance(col.type, Time) and isinstance(value, str):
            coerced[col.name] = time_type.fromisoformat(value)
        else:
            coerced[col.name] = value
    return coerced


def export_backup() -> BytesIO:
    """Returns a BytesIO of a JSON backup covering every table, in FK-safe order."""
    data: Dict[str, Any] = {
        "backup_format": "shaheen-erp-json-v1",
        "generated_at": datetime.utcnow().isoformat(),
        "tables": {},
    }

    with engine.connect() as conn:
        for table in Base.metadata.sorted_tables:
            rows = conn.execute(table.select()).mappings().all()
            data["tables"][table.name] = [dict(row) for row in rows]

    buffer = BytesIO(json.dumps(data, default=_json_default, indent=2).encode("utf-8"))
    buffer.seek(0)
    return buffer


def restore_backup(db: Session, backup_data: dict) -> Dict[str, int]:
    """
    Wipes and reloads every table from a previously exported JSON backup.
    Runs inside the given session's transaction — if anything fails, the
    whole restore rolls back and the database is left untouched.
    """
    if backup_data.get("backup_format") != "shaheen-erp-json-v1":
        raise ValueError("Unrecognized backup file format")

    tables_data = backup_data.get("tables", {})
    row_counts: Dict[str, int] = {}

    connection = db.connection()

    for table in reversed(Base.metadata.sorted_tables):
        connection.execute(table.delete())

    for table in Base.metadata.sorted_tables:
        rows = tables_data.get(table.name, [])
        row_counts[table.name] = len(rows)
        if not rows:
            continue
        coerced_rows = [_coerce_row_for_insert(table, row) for row in rows]
        connection.execute(insert(table), coerced_rows)

    db.commit()
    return row_counts
