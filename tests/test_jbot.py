import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jbot.access import check_paid_repair_access
from jbot.ai import OllamaUnavailable, _local_chat_url, is_paid_repair_request
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


class AiGateTests(unittest.TestCase):
    def test_repair_intents_are_paid(self):
        self.assertTrue(is_paid_repair_request("Please repair my phone"))
        self.assertTrue(is_paid_repair_request("show firmware flashing steps"))
        self.assertTrue(is_paid_repair_request("How do I factory reset this phone?"))

    def test_basic_diagnostics_remain_free(self):
        self.assertFalse(is_paid_repair_request("Why is my USB device not detected?"))
        self.assertFalse(is_paid_repair_request("What does Android version mean?"))

    def test_remote_inference_url_is_rejected(self):
        with patch.dict(os.environ, {"JBOT_OLLAMA_URL": "https://example.com/api/chat"}):
            with self.assertRaises(OllamaUnavailable):
                _local_chat_url()

    def test_billing_defaults_to_locked(self):
        env = {k: v for k, v in os.environ.items()
               if k not in {"JBOT_BILLING_URL", "JBOT_SESSION_TOKEN"}}
        with patch.dict(os.environ, env, clear=True):
            paid, reason = check_paid_repair_access("repair-123")
        self.assertFalse(paid)
        self.assertIn("not configured", reason.lower())


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
