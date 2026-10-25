"""Deterministic, non-destructive connection troubleshooting."""
def recommend() -> list[dict[str, str]]:
    return [
        {"id": "cable-port", "priority": "high", "title": "Check cable and USB port",
         "action": "Use a known data-capable cable, connect directly to the computer, and try another USB port.", "risk": "low"},
        {"id": "power-reconnect", "priority": "high", "title": "Check power and reconnect",
         "action": "Ensure the device has charge, unlock it if appropriate, disconnect, wait 10 seconds, and reconnect.", "risk": "low"},
        {"id": "authorization", "priority": "medium", "title": "Confirm device authorization",
         "action": "Approve the device's USB/debugging prompt only when you own it or have explicit service authorization.", "risk": "low"},
        {"id": "driver-status", "priority": "medium", "title": "Inspect host driver status",
         "action": "On Windows, inspect Device Manager for warning icons and use a verified driver for the exact model.", "risk": "low"},
        {"id": "preserve-data", "priority": "critical", "title": "Preserve customer data",
         "action": "Do not factory-reset, unlock a bootloader, flash firmware, or erase data without verified compatibility, authorization, backup status, and explicit approval.", "risk": "safety-gate"},
    ]
