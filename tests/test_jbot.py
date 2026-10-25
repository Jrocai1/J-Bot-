import sqlite3
import tempfile
import unittest
from pathlib import Path
from jbot.diagnostics import recommend
from jbot.storage import AuditStore

class DiagnosticsTests(unittest.TestCase):
    def test_recommendations_are_nonempty_and_non_destructive(self):
        items = recommend()
        self.assertGreaterEqual(len(items), 4)
        self.assertTrue(all(item.get("action") for item in items))
        self.assertTrue(any(item["id"] == "preserve-data" for item in items))

    def test_diagnostics_do_not_offer_security_bypass(self):
        combined = " ".join(item["action"].lower() for item in recommend())
        self.assertNotIn("bypass activation lock", combined)
        self.assertNotIn("bypass frp", combined)

class StorageTests(unittest.TestCase):
    def test_records_audit_event(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "jbot.sqlite3"
            AuditStore(db).record("test", {"count": 1})
            with sqlite3.connect(db) as conn:
                row = conn.execute("SELECT event_type, payload_json FROM audit_events").fetchone()
            self.assertEqual(row[0], "test")
            self.assertIn('"count": 1', row[1])

if __name__ == "__main__":
    unittest.main()
