"""Read-only phone and tablet triage. Does not bypass account protections or flash firmware."""
class ExpansionPack:
    def __init__(self):
        self.name = "Phone & Tablet Diagnostics"

    def run_diagnostics(self, payload):
        brand = str(payload.get("brand", "unknown"))[:100]
        model = str(payload.get("model", "not provided"))[:120]
        os_version = str(payload.get("os_version", "not provided"))[:80]
        symptom = str(payload.get("symptom", "not provided"))[:400]
        error_code = str(payload.get("error_code", "not provided"))[:80
]
        checks = [
            "Confirm exact model, regional variant, OS/build version, and available storage before choosing a procedure.",
            "Try a known data-capable cable and direct USB port; record whether the host detects a device.",
            "Use the official manufacturer tool and documentation appropriate to this exact model.",
            "Preserve user data and confirm a verified backup before any reset, restore, or firmware operation.",
            "No repair was executed or independently verified by this diagnostic request.",
        ]
        symptom_lower = symptom.lower()
        if any(word in symptom_lower for word in ("frp", "activation lock", "locked out", "forgot password")):
            checks.insert(0, "Use official account recovery and proof-of-ownership support. J-Bot will not bypass FRP, activation locks, passwords, or encryption.")
        if any(word in symptom_lower for word in ("bootloop", "stuck on logo", "won't boot")):
            checks.insert(0, "Record the exact recovery/download mode and error. Do not flash until model, region, bootloader revision, package integrity, and recovery path are verified.")
        return {
            "status": "diagnostic_guidance",
            "sector": "phone_gadget_fixer",
            "device": {"brand": brand, "model": model, "os_version": os_version},
            "symptom": symptom,
            "error_code": error_code,
            "recommendations": checks,
            "repair_status": "not_performed",
        }
