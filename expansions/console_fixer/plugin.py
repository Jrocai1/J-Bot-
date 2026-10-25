"""Non-invasive console diagnostics; no unsupported board-level instructions."""
class ExpansionPack:
    def __init__(self):
        self.name = "Video Game Console Diagnostics"

    def run_diagnostics(self, payload):
        console = str(payload.get("console_type", payload.get("brand", "unknown console"))).strip()[:100]
        model = str(payload.get("model", "not provided")).strip()[:120]
        symptom = str(payload.get("symptom", "not provided")).strip()[:300]
        error_code = str(payload.get("error_code", "not provided")).strip()[:80]
        recommendations = [
            "Confirm the exact console model, OS version, on-screen error code, and LED/blink pattern.",
            "Check the wall outlet, approved power adapter, external cables, ventilation, and external accessories.",
            "Try a known-good HDMI cable/display input if the symptom is no picture; do not assume a specific chip has failed.",
            "Use only the manufacturer's official system update or recovery package for the exact model, after checking data-loss implications.",
            "If liquid damage, burning odor, abnormal heat, or internal power faults are suspected, stop using it and refer it to a qualified technician.",
            "No hardware measurements, firmware writes, or repair actions were executed by this request.",
        ]
        low = symptom.lower()
        if any(word in low for word in ("no boot", "no power", "won't charge", "not charging")):
            recommendations.insert(0, "Begin with external power supply and cable checks; a symptom alone cannot identify a charging IC or board-level fault.")
        if any(word in low for word in ("black screen", "blue light", "no video", "no display")):
            recommendations.insert(0, "Check display input and external HDMI connections before inferring an internal video-path fault.")
        return {
            "status": "diagnostic_guidance",
            "sector": "console_fixer",
            "device": {"console_type": console, "model": model},
            "symptom": symptom,
            "error_code": error_code,
            "recommendations": recommendations,
            "repair_status": "not_performed",
        }
