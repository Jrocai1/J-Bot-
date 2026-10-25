"""Contactless e-bike and e-scooter telemetry triage; no bypass or guessed wiring advice."""
class ExpansionPack:
    def __init__(self):
        self.name = "E-Bike & E-Scooter Diagnostics"

    def run_diagnostics(self, payload):
        brand = str(payload.get("brand", "unknown"))[:100]
        model = str(payload.get("model", "not provided"))[:120]
        code = str(payload.get("fault_code", "not provided"))[:80]
        symptom = str(payload.get("symptom", "not provided"))[:400]
        reported_voltage = payload.get("voltage", "not supplied")
        recommendations = [
            "Controller fault codes and wire colors are manufacturer-specific. Verify the exact vehicle, display, controller revision, and official service documentation.",
            "Treat submitted voltage values as user-provided data; J-Bot has not measured voltage or validated the instrument.",
            "Do not bridge wires, bypass brake/throttle/ignition/NFC interlocks, change speed-limit protections, or guess phase/Hall combinations.",
            "Do not flash a controller unless firmware, hardware revision, battery/voltage class, package integrity, and recovery procedure are verified.",
            "If there is smoke, fire, swelling, leaking, sparking, or unusual battery heat: stop use and charging, keep clear, and contact qualified service or emergency services for an active fire.",
            "No controller command or physical repair was executed by this diagnostic request.",
        ]
        low = (symptom + " " + str(payload.get("condition", ""))).lower()
        if any(w in low for w in ("smoke", "swollen battery", "burning smell", "sparking", "battery hot", "leaking")):
            recommendations.insert(0, "SAFETY STOP: keep people clear. Do not open or handle a damaged lithium battery pack.")
        return {
            "status": "diagnostic_guidance",
            "sector": "ebike_ev_fixer",
            "device": {"brand": brand, "model": model},
            "reported_fault_code": code,
            "reported_voltage": reported_voltage,
            "symptom": symptom,
            "recommendations": recommendations,
            "repair_status": "not_performed",
        }
