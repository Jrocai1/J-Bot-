"""Local SQLite audit storage for J-Bot."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

class AuditStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )""")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def record(self, event_type: str, payload: dict) -> None:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute("INSERT INTO audit_events (created_at, event_type, payload_json) VALUES (?, ?, ?)",
                         (created_at, event_type, json.dumps(payload, sort_keys=True)))
