from __future__ import annotations
import unittest

from expansions.phone_gadget_fixer.plugin import ExpansionPack as PhonePack
from expansions.ebike_ev_fixer.plugin import ExpansionPack as EBiKEPack
from expansions.console_fixer.plugin import ExpansionPack as ConsolePack
from expansions.usb_serial_monitor.plugin import ExpansionPack as SerialPack


class ExpansionTests(unittest.TestCase):
    def test_phone_diagnostic_does_not_invent_battery_health(self):
        result = PhonePack().run_diagnostics({"model": "Example", "symptom": "bootloop"})
        self.assertEqual(result["repair_status"], "not_performed")
        self.assertNotIn("89%", str(result))
        self.assertTrue(result["recommendations"])

    def test_account_lock_is_not_bypassed(self):
        result = PhonePack().run_diagnostics({"symptom": "FRP locked"})
        self.assertIn("will not bypass", " ".join(result["recommendations"]).lower())

    def test_ebike_diagnostic_prohibits_wire_bypass(self):
        result = EBiKEPack().run_diagnostics({"fault_code": "0x04", "model": "unknown"})
        self.assertTrue(any("do not bridge wires" in item.lower() for item in result["recommendations"]))
        self.assertEqual(result["repair_status"], "not_performed")

    def test_console_diagnostic_does_not_claim_component_fault(self):
        result = ConsolePack().run_diagnostics({"console_type": "nintendo switch", "symptom": "no charge"})
        self.assertIn("diagnostic_guidance", result["status"])
        self.assertEqual(result["repair_status"], "not_performed")

    def test_serial_plugin_starts_with_inventory_not_streaming(self):
        result = SerialPack().run_diagnostics({})
        self.assertIn(result["status"], {"inventory_complete", "dependency_missing"})
        self.assertEqual(result.get("bytes_written", 0), 0)


if __name__ == "__main__":
    unittest.main()
